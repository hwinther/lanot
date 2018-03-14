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
