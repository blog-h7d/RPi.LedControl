class GPIO:
    BCM = 1
    OUT = 1
    LOW = 0
    HIGH = 1

    @staticmethod
    def setmode(mode):
        return True

    @staticmethod
    def setup(mode, *args, **kwargs):
        return True

    @staticmethod
    def output(*args):
        return True

    @staticmethod
    def cleanup():
        return True
