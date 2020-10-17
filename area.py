import asyncio

try:
    import neopixel
except NotImplementedError:
    from rpi_mock import neopixel

import calculator


class Area:

    def __init__(self, name: str):
        self.mode = 0
        self.name = name
        self.calculator = None
        self._strips = list()
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

        self._strips.append(strip)

    async def set_mode(self, mode, color1, color2):
        if not color1:
            color1 = (255, 0, 0, 0)

        if not color2:
            color2 = (0, 0, 255, 0)

        if 0 <= mode < 10:
            self.mode = mode
            if self.calculator and self._isActive:
                await self.calculator.stop()

            self._isActive = False

            if mode == 1:  # ColorWipe
                self.calculator = calculator.OneColorCalculator(self.get_number_of_pixel(), color1)
                self._isActive = True
            if mode == 2:
                self.calculator = calculator.ColorWipe(self.get_number_of_pixel(), color1)
                self._isActive = True
            if mode == 3:
                self.calculator = calculator.TestCounter(self.get_number_of_pixel())
                self._isActive = True

            if self.calculator and self._isActive:
                await self.calculator.start()
                asyncio.create_task(self._update_strips())

    async def _update_strips(self):
        while self._isActive and self.mode > 0 and self.calculator:
            start = 0
            for strip in self._strips:
                if strip['strip']:
                    for i in range(strip['start'], strip['end'], 1 if strip['start'] < strip['end'] else -1):
                        strip['strip'].setPixelColor(i, neopixel.Color(*self.calculator._data[start]))
                        start += 1
                    strip['strip'].show()
            else:
                start += abs(strip['start'] - strip['end'])

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
        for strip in self._strips:
            num_of_pixel += abs(strip['start'] - strip['end'])
        return num_of_pixel
