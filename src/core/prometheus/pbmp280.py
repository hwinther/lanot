# coding=utf-8
import prometheus
import machine
import bmp280
import gc

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class Bmp280(prometheus.Prometheus):
    def __init__(self, i2c):
        """
        :type i2c: machine.I2C
        """
        prometheus.Prometheus.__init__(self)
        self.bmp280 = bmp280.BMP280(i2c=i2c)

    # TODO: perhaps separate or add additional methods to get each of these values by themselves
    @prometheus.Registry.register('BMP280', 'v', str)
    def value(self, **kwargs):
        return '%f %f %f' % (self.bmp280.getTemp(), self.bmp280.getPress(), self.bmp280.getAltitude())
