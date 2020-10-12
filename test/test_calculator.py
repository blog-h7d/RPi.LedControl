import calculator
import pytest
import asyncio


def test_calculator_init():
    calc = calculator.CalculatorBase(10)
    assert calc._data == [calculator.CalculatorBase.BLACK] * 10


@pytest.mark.asyncio
async def test_color_wipe_calculate():
    color = (100, 100, 100, 100)
    wipe = calculator.ColorWipe(10, color)
    await wipe.start()
    assert wipe._data[0] == calculator.CalculatorBase.BLACK
    assert wipe._data[9] == calculator.CalculatorBase.BLACK

    await asyncio.sleep(1)
    assert wipe._data[0] == color
    assert wipe._data[9] == calculator.CalculatorBase.BLACK

    await asyncio.sleep(2)
    assert wipe._data[9] == calculator.CalculatorBase.BLACK

    await wipe.stop()
