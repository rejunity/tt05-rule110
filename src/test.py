import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

RULE110_TRUTH_TABLE = [0,1,1,1, 0,1,1,0]

# Python Rule110 by https://github.com/CarlosLunaMota/Rule110
# Used here to as an altenative implementation to test against
def Rule110(universe):
    """Performs a single iteration of the Rule 110 in a borderless universe."""
    new = set()
    for x in universe:
        if x+1 not in universe: new.add(x)
        if x-1 not in universe: new.add(x); new.add(x-1)
    return new

def print_automaton_state(dut):
    try:
        internal = dut.tt_um_rejunity_rule110_uut
        print(
            str(internal.cells.value).replace('0', ' ').replace('1', '@'),
            "in:",   dut.ui_in.value,
            "ctrl:", dut.uio_in.value,
            "out:",  dut.uo_out.value)
    except: # No access to internal state during the Gate Level simulation,
            # so we are just going to silently ignore exception and
            # print only outputs pins instead
        print(dut.uo_out.value)

def ctrl_FREE (): return -1                         # ALLOWS execution            inputs are freed - not driven
def ctrl_EXEC (rd_addr): return rd_addr << 2 | 0b11 # ALLOWS execution
def ctrl_HALT (rw_addr): return rw_addr << 2 | 0b01 # PAUSES execution            only HALT_n pulled low
def ctrl_WRITE(wr_addr): return wr_addr << 2 | 0b00 # PAUSES execution & WRITES   both WE_n and HALT_n pulled low for write

async def reset(dut):
    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut.uio_in.value = ctrl_FREE()

async def done(dut):
    dut.uio_in.value = ctrl_FREE()
    await ClockCycles(dut.clk, 1)
    # dut._log.info("DONE!")

### TESTS

@cocotb.test()
async def test_state_after_reset(dut):
    await reset(dut)

    dut._log.info(f'halting execution after reset')
    dut.uio_in.value = ctrl_HALT(0)
    await ClockCycles(dut.clk, 1)

    inner_state_after_reset = 1
    expected_output_after_reset =   (RULE110_TRUTH_TABLE[inner_state_after_reset << 1]     ) | \
                                    (RULE110_TRUTH_TABLE[inner_state_after_reset     ] << 1) | \
                                    (RULE110_TRUTH_TABLE[inner_state_after_reset >> 1] << 2)
    dut._log.info(f'inner state {inner_state_after_reset:08b} '
                                ''  '' f'=> expected output {expected_output_after_reset:08b}')
    dut._log.info(f'                        read values are {int(dut.uo_out.value):08b}')
    assert dut.uo_out.value == expected_output_after_reset
    await done(dut)

@cocotb.test()
async def test_halt_and_resume(dut):
    await reset(dut)

    dut._log.info(f'halting execution after reset')
    dut.uio_in.value = ctrl_HALT(0)
    output_while_halted = dut.uo_out.value

    dut._log.info("inner state and output should not change while halted")
    for i in range(10):
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value == output_while_halted
    dut._log.info(f'read values are {int(dut.uo_out.value):08b}')

    dut._log.info("automata should continue and output evolve after resume")
    dut.uio_in.value = ctrl_EXEC(0)
    previous_output = output_while_halted
    await ClockCycles(dut.clk, 1)
    for i in range(10):
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value != previous_output
        previous_output = dut.uo_out.value
    dut._log.info(f'read values are {int(dut.uo_out.value):08b}')
    await done(dut)

@cocotb.test()
async def test_rule110_truthtable_one_pattern_at_a_time(dut):
    await reset(dut)

    dut.uio_in.value = ctrl_WRITE(0) # constantly write to 0 address
    for i in range(8):
        dut._log.info(f'test pattern {i:03b} => {RULE110_TRUTH_TABLE[i]}')
        dut.ui_in.value = i
        await ClockCycles(dut.clk, 2) # 1st cycle to set inputs, 2nd cycle to propogate the output
        assert dut.uo_out.value[6] == RULE110_TRUTH_TABLE[i]
    await done(dut)

@cocotb.test()
async def test_rule110_truthtable_all_patterns_in_parallel(dut):
    await reset(dut)

    # prepare patterns
    all_patterns = 0
    all_truths = 0
    all_truths_mask = 0
    for i in range(8):
        all_patterns <<= 3
        all_patterns |= (i & 0x7)

        all_truths <<= 3
        all_truths_mask <<= 3
        all_truths |= RULE110_TRUTH_TABLE[i] << 1
        all_truths_mask |= 0b010
    dut._log.info(f'test patterns {all_patterns:024b}')
    dut._log.info(f'         mask {all_truths_mask:024b}')
    dut._log.info(f'       truths {all_truths:024b}')

    dut._log.info("write patterns to inputs")
    for addr in range(3): # 3 blocks of 8 cells
        dut.uio_in.value = ctrl_HALT(addr)
        dut.ui_in.value = all_patterns & 0xff
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = ctrl_WRITE(addr)
        await ClockCycles(dut.clk, 2)
        print_automaton_state(dut)
        all_patterns >>= 8

    dut._log.info("read answers from outputs")
    all_answers = 0
    for addr in range(3, 0, -1): # 3 blocks of 8 cells
        dut.uio_in.value = ctrl_HALT(addr - 1)
        await ClockCycles(dut.clk, 1)
        all_answers <<= 8
        all_answers |= dut.uo_out.value
    dut._log.info(f'read values are {all_answers:024b}')
    dut._log.info(f'   mask applied {(all_answers & all_truths_mask):024b}')

    assert all_answers & all_truths_mask == all_truths
    await done(dut)

def show(universe, window, alive='■', dead=' ', space=' '):
        """Prints a segment of the universe on the screen."""

        print(''.join(alive if x in universe else dead for x in range(*window)))

def compare(dut, universe):
    state = dut.uo_out.value
    for i in range(1, 9):
        cell_index_in_alternative_rule110_impl = -i # for some reason Carlos Luna Mota implementation
                                                    # uses negative indices to mark alive cells
        if state[8-i] != 0: # is dead or alive
            assert cell_index_in_alternative_rule110_impl in universe 
        else:
            assert cell_index_in_alternative_rule110_impl not in universe

@cocotb.test()
async def test_rule110_automata_run_from_reset(dut):
    await reset(dut)

    universe   = {-1}   # alternative implementation by Carlos Luna Mota to test against
                        # NOTE: Carlos implementation is infinite, does not provide looping

    dut._log.info("run")
    for i in range(128-1):
    # for i in range(128+32):
    # for i in range(32):
        await ClockCycles(dut.clk, 1)
        # show(universe, (-129, 0))
        universe = Rule110(universe)
        compare(dut, universe)
        print_automaton_state(dut)

# TODO test, start from a new state
# TODO test, all outputs against Carlos impl not just 8 rightmost cells


    # dut._log.info("setup")
    # dut.ui_in.value = 19 # <<7
    # dut.uio_in.value = 0b11_1111_10
    # dut.uio_in.value = 0b00_0001_10
    # dut.uio_in.value = 0b00_0000_10
    # await ClockCycles(dut.clk, 1)
    # dut.uio_in.value = -1

    # # dut.uio_in.value = 0b001
    # #dut.ui_in.value = 0b11100
    # #dut.uio_in.value[0] = 0 # 0b0000_0101
    # await ClockCycles(dut.clk, 1)
    # print(str(dut.tt_um_rejunity_rule110_uut.cells.value).replace('0', ' ').replace('1', '@'))
    # print("",str(dut.tt_um_rejunity_rule110_uut.cells_dt.value).replace('0', ' ').replace('1', '@'))
    # dut.ui_in.value = 0b101 # <<7
    # await ClockCycles(dut.clk, 1)
    # print(str(dut.tt_um_rejunity_rule110_uut.cells.value).replace('0', ' ').replace('1', '@'))
    # print("",str(dut.tt_um_rejunity_rule110_uut.cells_dt.value).replace('0', ' ').replace('1', '@'))


    dut._log.info("done")

    print((''.join(format(ord(i), '08b') for i in "Hello, world")).replace('0', ' ').replace('1', '@'))
    print((''.join(format(ord(i), '08b') for i in "hello world!")).replace('0', ' ').replace('1', '@'))
