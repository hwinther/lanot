import machine


class NeoPixel(object):
    ORDER = (1, 0, 2, 3)

    def __init__(self, pin, n, bpp=3):
        self.pin = pin
        self.n = n
        self.bpp = bpp
        self.buf = bytearray(n * bpp)
        assert isinstance(self.pin, machine.Pin)
        self.pin.init(pin.OUT)

    def __setitem__(self, index, val):
        offset = index * self.bpp
        for i in range(self.bpp):
            self.buf[offset + self.ORDER[i]] = val[i]

    def __getitem__(self, index):
        offset = index * self.bpp
        return tuple(self.buf[offset + self.ORDER[i]]
                     for i in range(self.bpp))

    def fill(self, color):
        for i in range(self.n):
            self[i] = color

    def write(self):
        print('neopixel_write(self.pin=%s, self.buf=%s, True' % (self.pin, self.buf))
