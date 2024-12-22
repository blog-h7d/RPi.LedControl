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
        self._strips: list = []
        self._isActive = False

    def add_strip(self, start: int, end: int, strip: neopixel.NeoPixel | None = None):
        if start < 0:
            raise ValueError("Start must be >= 0")

        if end < 0:
            raise ValueError("End must be >= 0")

        if start == end:
            raise ValueError("Start and end must be different")

        self._strips.append({
            'start': start,
            'end': end,
            'strip': strip
        })

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
            if mode == 4:
                self.calculator = calculator.FireCalc(self.get_number_of_pixel())
                self._isActive = True

            if self.calculator and self._isActive:
                await self.calculator.start()
                asyncio.create_task(self._update_strips())

    def _set_color(self, strip: neopixel.NeoPixel, start, end, colors: list):
        strip[start:end] = colors

    async def _update_strips(self):
        async def update():
            if not self.calculator:
                return

            data = self.calculator.data
            start = 0
            for act_strip in self._strips:
                if np := act_strip['strip']:
                    length = abs(act_strip['end'] - act_strip['start'])
                    if act_strip['start'] < act_strip['end']:
                        self._set_color(np, act_strip['start'], act_strip['end'], data[start: start + length])
                    else:
                        self._set_color(np, act_strip['end'], act_strip['start'],
                                        data[start + length - 1: start - 1:-1])
                    start += length
                    np.show()

        while self._isActive and self.mode > 0 and self.calculator:
            await asyncio.gather(asyncio.sleep(0.1), update())

        for strip in self._strips:
            if np := strip['strip']:
                self._set_color(np,
                                min(strip['start'], strip['end']),
                                max(strip['start'], strip['end']),
                                (0, 0, 0, 0) * abs(strip['end'] - strip['start']))

    async def stop(self):
        self._isActive = False
        if self.calculator:
            await self.calculator.stop()

    def get_number_of_pixel(self):
        num_of_pixel = 0
        for strip in self._strips:
            num_of_pixel += abs(strip['start'] - strip['end'])
        return num_of_pixel
