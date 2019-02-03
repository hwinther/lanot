# coding=utf-8
import prometheus
import machine
import hdc1080
import gc

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class Hdc1080(prometheus.Prometheus):
    def __init__(self, i2c, addr=0x40):
        """
        0x40 = 64
        :type i2c: machine.I2C
        :type addr: int
        """
        prometheus.Prometheus.__init__(self)
        self.hdc1080 = hdc1080.HDC1000(i2c=i2c, addr=addr)

    # TODO: perhaps separate or add additional methods to get each of these values by themselves
    @prometheus.Registry.register('HDC1080', 'v', str)
    def value(self, **kwargs):
        return '%f %f' % (self.hdc1080.read_temperature(), self.hdc1080.read_humidity())
