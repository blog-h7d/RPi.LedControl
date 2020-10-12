class ws:
    SK6812_STRIP_GRBW = 1


def Color(red, green, blue, white=0):
    return (white << 24) | (red << 16) | (green << 8) | blue


class NeoPixel:
    def __init__(self, *args, **kwargs):
        pass

    def begin(self):
        pass
