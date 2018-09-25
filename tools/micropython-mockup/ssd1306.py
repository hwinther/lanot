import prometheus.logging as logging


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class SSD1306_I2C(object):
    def __init__(self, width, height, i2c, addr=60):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr

    def text(self, txt, x, y):
        logging.debug('Setting text %s at %d,%d' % (txt, x, y))

    def show(self):
        logging.debug('Showing on lcd')

    def fill(self, value):
        logging.debug('Fill with %s' % value)

    def invert(self, invert):
        logging.debug('Inverting pixels')

    def contrast(self, contrast):
        logging.debug('Setting contrast')

    def pixel(self, x, y, col):
        logging.debug('Setting pixel at %d.%d' % (x, y))

    def scroll(self, dx, dy):
        logging.debug('Scrolling')

    def poweroff(self):
        logging.debug('Poweroff display')

    def init_display(self):
        logging.debug('init_display')
