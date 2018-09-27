# coding=utf-8
import prometheus
import machine
import ads1x15
import gc

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class ADS1115(prometheus.Prometheus):
    def __init__(self, i2c, addr=0x48):
        """
        0x48 = 72
        :type i2c: machine.I2C
        :type addr: int
        """
        prometheus.Prometheus.__init__(self)
        self.ads1115 = ads1x15.ADS1115(i2c=i2c, address=addr)

    @prometheus.Registry.register('ADS1115', 'v', 'OUT')
    def read(self, **kwargs):
        return '%d %d %d %d' % (self.ads1115.read(0, 0), self.ads1115.read(1, 0),
                                self.ads1115.read(2, 0), self.ads1115.read(3, 0))
