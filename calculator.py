import asyncio
import copy
import itertools
import random

import typing
from unittest import case

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

        self._data = [self.black for _ in range(self.length)]
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
        self.active_length = length // 10

    async def _calculate(self):
        act_pos = 0
        self._is_running = True
        while self._is_active:
            start_black = max(0, act_pos + self.active_length - self.length)
            self._data = [self.color] * start_black + \
                         [self.black] * (start_black + act_pos) + \
                         [self.color] * (self.active_length - start_black) + \
                         [self.black] * (self.length - (self.active_length + act_pos))

            act_pos = (act_pos + 1) % self.length

            await asyncio.sleep(0.1)


class TestCounter(CalculatorBase):
    name = "test"

    def __init__(self, length: int):
        super().__init__(length)

    async def _calculate(self):
        act_pos = 0
        while self._is_active:
            self._data = [self.black] * self.length
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
        self.number_of_random = length // 25
        self.cycle_time = 0.1

    def _set_color(self, number, add_red: int, add_green: int, add_blue: int = 0, add_white: int = 0):
        for index in random.sample(range(self.length), k=number):
            self._data[index][0] = min(self._data[index][0] + add_red, 255)
            self._data[index][1] = min(self._data[index][1] + add_green, 255)
            self._data[index][2] = min(self._data[index][2] + add_blue, 255)
            self._data[index][3] = min(self._data[index][3] + add_white, 255)

    async def _calculate(self):
        self._data = [[0, 0, 0, 0] for _ in range(self.length)]

        self._set_color(self.number_of_random, 40, 4, 0)

        while self._is_active:
            await asyncio.gather(asyncio.sleep(self.cycle_time), self._update_color())

    async def _update_color(self):
        self._set_color(self.number_of_random // 2, 60, 10, 0, 20)
        self._set_color(self.number_of_random, 50, 20, 10)
        self._set_color(self.number_of_random // 2, 50, 25, 0, 10)

        old_colors = copy.copy(self._data)
        for i in range(self.length):
            act = old_colors[i]
            right = old_colors[(i + 1) % self.length]
            left = old_colors[(i - 1) % self.length]
            self._data[i] = [
                max(right[0] // 6 + act[0] * 2 // 3 + left[0] // 6 - 5, 0),
                max(right[1] // 6 + act[1] * 2 // 3 + left[1] // 6 - 8, 0),
                max(right[2] // 6 + act[2] * 2 // 3 + left[2] // 6 - 10, 0),
                max(right[3] // 6 + act[3] * 2 // 3 + left[3] // 6 - 15, 0),
            ]


class PartyCalc(CalculatorBase):
    name = "party"

    def __init__(self, length: int):
        super().__init__(length)
        self.spots = [[0, 0] for _ in range(length // 10 + 1)]
        self.cycle_time = 0.1

    def _get_color(self, color_code: int) -> ColorRGBX:
        match color_code:
            case 0:
                return self.black
            case 1:
                return 255, 0, 0, 0
            case 2:
                return 0, 255, 0, 0
            case 3:
                return 0, 0, 255, 0
            case 4:
                return 255, 0, 255, 0
            case 5:
                return 255, 255, 0, 0
            case 6:
                return 255, 128, 0, 0
            case 7:
                return 0, 128, 255, 0

        return self.black

    async def _calculate(self):
        self._data = [[0, 0, 0, 0] for _ in range(self.length)]

        while self._is_active:
            await asyncio.gather(asyncio.sleep(self.cycle_time), self._update_color())

    async def _update_color(self):
        for spot in self.spots:
            if spot[1] <= 0:
                spot[0] = random.randint(0, 12)
                spot[1] = random.randint(10, 30)
            spot[1] = spot[1] - 1

        self._data = list(itertools.chain(
            *[[self._get_color(spot[0])] * 10 for spot in self.spots]
        ))[0:self.length]
        print(len(self.spots), len(self._data), self.length)
