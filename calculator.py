import asyncio
import copy
import random

import typing

ColorRGBX = typing.NewType("ColorRGBX", (int, int, int, int))


class CalculatorBase:
    name = ""
    cycle_time = 0.2

    def __init__(self, length: int):
        self.length = length
        self._data: list = [CalculatorBase.black] * length
        self._is_active = False
        self._is_running = False

    @property
    def black(self) -> list:
        return [0, 0, 0, 0]

    @property
    def data(self) -> list[tuple[int, int, int, int]]:
        return [(x[0], x[1], x[2], x[3]) for x in self._data if len(x) >= 4]

    async def start(self):
        self._is_active = True
        asyncio.create_task(self._calculate())

    async def stop(self):
        self._is_active = False
        while self._is_running:
            await asyncio.sleep(0.1)

        self._data = [[0,0,0,0] for _ in range(self.length)]
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

    async def _calculate(self):
        act_pos = 0
        self._isRunning = True
        while self._is_active and act_pos < self.length:
            self._data = [self.color] * self.actPos + [CalculatorBase.black] * (self.length - self.actPos)
            act_pos += 1

            await asyncio.sleep(0.2)

        self._isRunning = False


class TestCounter(CalculatorBase):
    name = "test"

    def __init__(self, length: int):
        super().__init__(length)

    async def _calculate(self):
        act_pos = 0
        while self._is_active:
            self._data = [CalculatorBase.black] * self.length
            for i in range(0, self.length // 10):
                self._data[i * 10] = [0, 0, 255, 0]
                self._data[i * 10 + act_pos] = [0, 255, 0, 0]
            for i in range(0, self.length // 100):
                self._data[i * 100] = [255, 0, 0, 0]

            act_pos = (act_pos + 1) % 10
            await asyncio.sleep(1)


class FireCalc(CalculatorBase):
    name = "fire"

    def __init__(self, length: int):
        super().__init__(length)
        self.number_of_random = length // 20
        self.cycle_time = 0.3

    def _set_color(self, number, add_red: int, add_green: int, add_blue: int = 0):
        for index in random.sample(range(self.length), k=number):
            self._data[index][0] = min(self._data[index][0] + add_red, 255)
            self._data[index][1] = min(self._data[index][1] + add_green, 255)
            self._data[index][2] = min(self._data[index][2] + add_blue, 255)

    async def _calculate(self):
        self._data = [[0, 0, 0, 0] for _ in range(self.length)]

        self._set_color(self.number_of_random, 40, 4, 0)

        while self._is_active:
            await asyncio.gather(self._update_color(), asyncio.sleep(self.cycle_time))

    async def _update_color(self):
        self._set_color(self.number_of_random, 20, 0, 0)
        self._set_color(self.number_of_random // 2, 20, 10, 0)
        self._set_color(self.number_of_random // 2, 20, 20, 0)

        old_colors = copy.copy(self._data)
        for i in range(self.length):
            act = old_colors[i]
            right = old_colors[(i + 1) % self.length]
            left = old_colors[(i - 1) % self.length]
            self._data[i] = [
                max(right[0] // 4 + act[0] // 2 + left[0] // 4 - 1, 0),
                max(right[1] // 4 + act[1] // 2 + left[1] // 4 - 4, 0),
                max(right[2] // 4 + act[2] // 2 + left[2] // 4 - 8, 0),
                0
            ]
