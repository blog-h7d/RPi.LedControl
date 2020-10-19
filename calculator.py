import asyncio
import random

import typing


class Color:

    def __init__(self, red=0, green=0, blue=0, white=0):
        self.red = red
        self.green = green
        self.blue = blue
        self.white = white

    @property
    def hex_color_string(self) -> str:
        return f'#{"%02X" % self.red}{"%02X" % self.green}{"%02X" % self.blue}'

    @property
    def url_string(self) -> str:
        return f'{str(self.red)}.{str(self.green)}.{str(self.blue)}.{str(self.white)}'

    @property
    def percentage_white_value(self) -> float:
        return self.white / 255.0

    @property
    def strip_value(self) -> int:
        return (self.white << 24) | (self.red << 16) | (self.green << 8) | self.blue

    def __eq__(self, other):
        return isinstance(other, Color) and self.white == other.white \
               and self.red == other.red and self.green == other.green \
               and self.blue == other.blue

    def __str__(self):
        return self.hex_color_string


class CalculatorBase:
    name = ""
    number_of_colors = 0
    BLACK: Color = Color(0, 0, 0, 0)
    cycleTime = 0.2

    def __init__(self, length: int):
        self.length = length
        self.data: typing.List[Color] = [CalculatorBase.BLACK] * length
        self._isActive = False
        self._isRunning = False

    async def start(self):
        self._isActive = True
        asyncio.create_task(self._calculate())

    async def stop(self):
        self._isActive = False
        while self._isRunning:
            await asyncio.sleep(0.1)

        self.data = [CalculatorBase.BLACK] * self.length
        await asyncio.sleep(0.5)

    async def _calculate(self):
        raise NotImplemented()


class OneColorCalculator(CalculatorBase):
    name = "color"
    number_of_colors = 1

    def __init__(self, length, color: Color):
        super().__init__(length)
        self.color = color
        self.data = [color] * length

    async def _calculate(self):
        pass


class ColorWipe(CalculatorBase):
    name = "color_wipe"
    number_of_colors = 1

    def __init__(self, length: int, color: Color):
        super().__init__(length)
        self.color: Color = color
        self.actPos: int = 0

    async def _calculate(self):
        self.actPos = 0
        self._isRunning = True
        while self._isActive and self.actPos < self.length:
            self.data = [self.color] * self.actPos + [CalculatorBase.BLACK] * (self.length - self.actPos)
            self.actPos += 1

            await asyncio.sleep(0.2)

        self._isRunning = False


class TestCounter(CalculatorBase):
    name = "test"
    number_of_colors = 0

    def __init__(self, length: int):
        super().__init__(length)

    async def _calculate(self):
        act_pos = 0
        while self._isActive:
            self.data = [CalculatorBase.BLACK] * self.length
            for i in range(0, self.length // 10):
                self.data[i * 10] = Color(blue=255)
                self.data[i * 10 + act_pos] = Color(green=255)
            for i in range(0, self.length // 100):
                self.data[i * 100] = Color(red=255)

            act_pos = (act_pos + 1) % 10
            await asyncio.sleep(1)


class FireCalc(CalculatorBase):
    name = "fire"
    number_of_colors = 0

    def __init__(self, length: int):
        super().__init__(length)
        self.number_of_random = length // 20

    async def _calculate(self):
        self.data = [CalculatorBase.BLACK] * self.length
        for i in range(2*self.number_of_random):
            index = random.randrange(0, self.length, 1)
            self.data[index] = Color(red=min(self.data[index].red + 200, 255),
                                     green=min(self.data[index].green + 80, 255))
        while self._isActive:
            for i in range(self.number_of_random):
                index = random.randrange(0, self.length, 1)
                self.data[index] = Color(red=min(self.data[index].red + 200, 255),
                                         green=min(self.data[index].green + 80, 255))

            old_colors = self.data
            for i in range(self.length):
                act = old_colors[i]
                right = old_colors[(i + 1) % self.length]
                left = old_colors[(i - 1) % self.length]
                self.data[i] = Color(
                    red=max(right.red // 6 + act.red * 2 // 3 + left.red // 6 - 6, 0),
                    green=max(right.green // 12 + act.green * 5 // 6 + left.green // 12 - 4, 0)
                )

            await asyncio.sleep(0.5)
