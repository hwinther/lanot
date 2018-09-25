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

    def text(self, txt, x=0, y=0):
        self.ssd.fill(False)
        self.ssd.text(txt, x, y)
        self.ssd.show()

    def custom_command(self, command, reply, source, **kwargs):
        if not len(command) > 4 or not command[0:4] == 'ssd ':
            return prometheus.Prometheus.custom_command(self, command, reply, source, **kwargs)

        self.text(command[4:], 0, 0)

        gc.collect()
        return True
