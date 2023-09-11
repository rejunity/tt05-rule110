import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles


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
    dut.ui_in.value = 1 # <<7
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("run")
    for i in range(128+32):
        await ClockCycles(dut.clk, 1)
        print(
            str(dut.tt_um_rejunity_rule110_uut.cells_.value).replace('0', ' ').replace('1', '@'),
            dut.uio_out.value,
            dut.uo_out.value)

    dut._log.info("done")
