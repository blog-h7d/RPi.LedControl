import asyncio

import pytest

import calculator


def test_color_hex():
    blue = calculator.Color(blue=255)
    assert blue.hex_color_string == "#0000FF"

    green = calculator.Color(green=255)
    assert green.hex_color_string == "#00FF00"

    red = calculator.Color(red=255)
    assert red.hex_color_string == "#FF0000"

    white = calculator.Color(white=255)
    assert white.hex_color_string == "#000000"


def test_color_white_value():
    white = calculator.Color(white=255)
    assert white.percentage_white_value == 1

    half_white = calculator.Color(white=100)
    assert half_white.percentage_white_value == 100.0 / 255


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
