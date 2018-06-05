# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class SSD1306_I2C(object):
    def __init__(self, width, height, i2c):
        self.width = width
        self.height = height
        self.i2c = i2c

    def text(self, txt, x, y):
        print('Setting text %s at %d,%d' % (txt, x, y))

    def show(self):
        print('Showing on lcd')

    def fill(self, value):
        print('Fill with %s' % value)

    def invert(self, invert):
        print('Inverting pixels')

    def contrast(self, contrast):
        print('Setting contrast')

    def pixel(self, x, y, col):
        print('Setting pixel at %d.%d' % (x, y))

    def scroll(self, dx, dy):
        print('Scrolling')

    def poweroff(self):
        print('Poweroff display')

    def init_display(self):
        print('init_display')
