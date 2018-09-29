# coding=utf-8
import prometheus
import machine
import max7219
import gc

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class MAX7219(prometheus.Prometheus):
    ssd = None  # type: max7219.Matrix8x8

    def __init__(self, spi, cspin, matrixes=4):
        """
        0x3c = 60
        :type spi: machine.SPI
        :type cspin: machine.Pin
        :type matrixes: int
        """
        prometheus.Prometheus.__init__(self)
        self.max = max7219.Matrix8x8(spi, cspin, matrixes)
        self.max.brightness(0)

    @prometheus.Registry.register('MAX7219', 't', str)
    def text(self, text=None, x=0, y=0, value=1, **kwargs):
        if text is None:
            text = 'No text set'
        if not isinstance(x, int):
            x = int(x)
        if not isinstance(y, int):
            y = int(y)
        if not isinstance(value, int):
            value = int(value)
        self.max.fill(value ^ 1)
        self.max.text(text, x, y, value)
        self.max.show()
        # for confirmation & testing
        return text

    @prometheus.Registry.register('MAX7219', 'b', int)
    def brightness(self, value=0, **kwargs):
        if not isinstance(value, int):
            value = int(value)
        self.max.brightness(value)
        return value
