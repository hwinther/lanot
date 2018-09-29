# coding=utf-8
import prometheus
import machine
import ssd1306
import gc

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class SSD1306(prometheus.Prometheus):
    ssd = None  # type: ssd1306.SSD1306_I2C
    # TODO: add more function, such as those inherited from framebuf
    # TODO: perhaps use a common super class and share with simular devices

    def __init__(self, i2c, addr=0x3c, height=128, width=64):
        """
        0x3c = 60
        :type i2c: machine.I2C
        :type addr: int
        :type height: int
        :type width: int
        """
        prometheus.Prometheus.__init__(self)
        self.ssd = ssd1306.SSD1306_I2C(height, width, i2c, addr)

    @prometheus.Registry.register('SSD1306', 't', str)
    def text(self, text=None, x=0, y=0, **kwargs):
        if text is None:
            text = 'No text set'
        if not isinstance(x, int):
            x = int(x)
        if not isinstance(y, int):
            y = int(y)
        self.ssd.fill(False)
        self.ssd.text(text, x, y)
        self.ssd.show()
        # for confirmation & testing
        return text
