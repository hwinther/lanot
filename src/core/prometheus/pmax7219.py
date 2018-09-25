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

    def text(self, txt, x=0, y=0, value=1):
        if value:
            self.max.fill(0)
        else:
            self.max.fill(1)
        self.max.text(txt, x, y, value)
        self.max.show()

    def brightness(self, value):
        self.max.brightness(value)

    def custom_command(self, command, reply, source, **kwargs):
        if not len(command) > 4 or not command[0:4] == 'max ':
            return prometheus.Prometheus.custom_command(self, command, reply, source, **kwargs)

        self.text(command[4:], 0, 0)

        gc.collect()
        return True
