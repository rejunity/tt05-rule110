import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

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


# @cocotb.test()
async def test_rule110(dut):
    RULE110_TRUTH_TABLE = [0,1,1,1, 0,1,1,0]

    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("test against truth table")
    for i in range(8):
        dut._log.info(i)
        dut.ui_in.value = i
        await ClockCycles(dut.clk, 1)
        print(dut.uo_out.value)
        assert dut.uo_out.value[7] == RULE110_TRUTH_TABLE[i]

    dut._log.info("done")

@cocotb.test()
async def test_rule110_automata(dut):

    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    # print(str(dut.tt_um_rejunity_rule110_uut.cells.value).replace('0', ' ').replace('1', '@'))
    # print("",str(dut.tt_um_rejunity_rule110_uut.cells_dt.value).replace('0', ' ').replace('1', '@'))
    dut.rst_n.value = 1
    dut.uio_in.value = -1

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

    dut._log.info("run")
    for i in range(128+32):
    # for i in range(32):
        await ClockCycles(dut.clk, 1)
        print_automaton_state(dut)

    dut._log.info("done")

    print((''.join(format(ord(i), '08b') for i in "Hello, world")).replace('0', ' ').replace('1', '@'))
    print((''.join(format(ord(i), '08b') for i in "hello world!")).replace('0', ' ').replace('1', '@'))
