import asyncio

import pytest

import calculator


def test_calculator_init():
    calc = calculator.CalculatorBase(10)
    for entry in range(10):
        assert calc.data[entry] == calculator.CalculatorBase.BLACK


@pytest.mark.asyncio
async def test_color_wipe_calculate():
    color = calculator.Color(100, 100, 100, 100)
    wipe = calculator.ColorWipe(10, color)
    await wipe.start()
    assert wipe.data[0] == calculator.CalculatorBase.BLACK
    assert wipe.data[9] == calculator.CalculatorBase.BLACK

    await asyncio.sleep(2)
    assert wipe.data[0] == color, f"LED 0 is {wipe.data[0]} but should be {color}"
    assert wipe.data[9] == calculator.CalculatorBase.BLACK

    await asyncio.sleep(2)
    assert wipe.data[9] == calculator.CalculatorBase.BLACK

    await wipe.stop()
