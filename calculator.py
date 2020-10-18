import asyncio
import random

import typing

ColorRGBX = typing.NewType("ColorRGBX", (int, int, int, int))


class CalculatorBase:
    name = ""
    BLACK: ColorRGBX = (0, 0, 0, 0)
    cycleTime = 0.2

    def __init__(self, length: int):
        self.length = length
        self._data: typing.List[ColorRGBX] = [CalculatorBase.BLACK] * length
        self._isActive = False
        self._isRunning = False

    @property
    def data(self):
        return ", ".join([str(x) for x in self._data])

    async def start(self):
        self._isActive = True
        asyncio.create_task(self._calculate())

    async def stop(self):
        self._isActive = False
        while self._isRunning:
            await asyncio.sleep(0.1)

        self._data = [CalculatorBase.BLACK] * self.length
        await asyncio.sleep(0.5)

    async def _calculate(self):
        raise NotImplemented()


class OneColorCalculator(CalculatorBase):
    name = "color"

    def __init__(self, length, color: ColorRGBX):
        super().__init__(length)
        self.color = color
        self._data = [color] * length

    async def _calculate(self):
        pass


class ColorWipe(CalculatorBase):
    name = "color_wipe"

    def __init__(self, length: int, color: ColorRGBX):
        super().__init__(length)
        self.color: ColorRGBX = color
        self.actPos: int = 0

    async def _calculate(self):
        self.actPos = 0
        self._isRunning = True
        while self._isActive and self.actPos < self.length:
            self._data = [self.color] * self.actPos + [CalculatorBase.BLACK] * (self.length - self.actPos)
            self.actPos += 1

            await asyncio.sleep(0.2)

        self._isRunning = False


class TestCounter(CalculatorBase):
    name = "test"

    def __init__(self, length: int):
        super().__init__(length)

    async def _calculate(self):
        act_pos = 0
        while self._isActive:
            self._data = [CalculatorBase.BLACK] * self.length
            for i in range(0, self.length // 10):
                self._data[i * 10] = (0, 0, 255, 0)
                self._data[i * 10 + act_pos] = (0, 255, 0, 0)
            for i in range(0, self.length // 100):
                self._data[i * 100] = (255, 0, 0, 0)

            act_pos = (act_pos + 1) % 10
            await asyncio.sleep(1)


class FireCalc(CalculatorBase):
    name = "fire"

    def __init__(self, length: int):
        super().__init__(length)
        self.number_of_random = length // 20

    async def _calculate(self):
        self._data = [CalculatorBase.BLACK] * self.length
        while self._isActive:
            for i in range(self.number_of_random):
                index = random.randrange(self.length)
                self._data[index][0] = min(self._data[index][0] + 100, 255)
                self._data[index][1] = min(self._data[index][1] + 60, 255)

            old_colors = self._data
            for i in range(self.length):
                act = old_colors[i]
                right = old_colors[(i + 1) % self.length]
                left = old_colors[(i - 1) % self.length]
                self._data[i] = [max(right[0] // 6 + act[0] * 2 // 3 + left[0] // 6 - 2, 0),
                                 max(right[1] // 6 + act[1] * 2 // 3 + left[1] // 6 - 5, 0), 0]

            await asyncio.sleep(1)
