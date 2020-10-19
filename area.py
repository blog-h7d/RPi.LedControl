import asyncio

try:
    import neopixel
except NotImplementedError:
    from rpi_mock import neopixel

import calculator


class Area:

    def __init__(self, name: str):
        self.mode: str = "black"
        self.name = name
        self.calculator = None
        self.length = 0
        self.strips = list()
        self._isActive = False

    def add_strip(self, start: int, end: int, strip=None):
        if start < 0:
            raise ValueError("Start must be >= 0")

        if end < 0:
            raise ValueError("End must be >= 0")

        if start == end:
            raise ValueError("Start and end must be different")

        strip = {
            'start': start,
            'end': end,
            'strip': strip
        }

        self.length += abs(end - start)

        self.strips.append(strip)

    @staticmethod
    def _get_calculator(name: str) -> type:
        for calculator_class in calculator.CalculatorBase.__subclasses__():
            if calculator_class.name == name:
                return calculator_class

    async def set_mode(self, mode: str, color1: calculator.Color = None, color2: calculator.Color = None):
        if not color1:
            color1 = calculator.Color(255, 0, 0, 0)

        if not color2:
            color2 = calculator.Color(0, 0, 255, 0)

        self.mode = mode
        if self.calculator and self._isActive:
            await self.calculator.stop()

        self._isActive = False

        if mode != "black":
            calculator_class = self._get_calculator(mode)
            if calculator_class:
                if calculator_class.number_of_colors == 0:
                    self.calculator = calculator_class(self.get_number_of_pixel())
                    self._isActive = True
                if calculator_class.number_of_colors == 1:
                    self.calculator = calculator_class(self.get_number_of_pixel(), color1)
                    self._isActive = True
                if calculator_class.number_of_colors == 2:
                    self.calculator = calculator_class(self.get_number_of_pixel(), color1, color2)
                    self._isActive = True

        if self.calculator and self._isActive:
            await self.calculator.start()
            asyncio.create_task(self._update_strips())

    async def _update_strips(self):
        while self._isActive and self.mode != "black" and self.calculator:
            start = 0
            for strip_data in self.strips:
                if strip_data['strip']:
                    s = strip_data['strip']
                    for i in range(strip_data['start'], strip_data['end'],
                                   1 if strip_data['start'] < strip_data['end'] else -1):
                        s['strip'].setPixelColor(i, self.calculator.data[start].strip_value)
                        start += 1
                    s['strip'].show()
            else:
                start += abs(strip_data['start'] - strip_data['end'])

            await asyncio.sleep(0.2)

        for strip in self._strips:
            if strip['strip']:
                for i in range(strip['start'], strip['end'], 1 if strip['start'] < strip['end'] else -1):
                    strip['strip'].setPixelColor(i, neopixel.Color(0, 0, 0, 0))

    async def stop(self):
        self._isActive = False
        if self.calculator:
            await self.calculator.stop()

    def get_number_of_pixel(self):
        num_of_pixel = 0
        for strip in self.strips:
            num_of_pixel += abs(strip['start'] - strip['end'])
        return num_of_pixel
