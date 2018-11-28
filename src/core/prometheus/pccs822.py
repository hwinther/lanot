# coding=utf-8
import prometheus
import machine
import CCS811
import gc

__version__ = '0.1.1'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class Ccs811(prometheus.Prometheus):
    def __init__(self, i2c, addr=0x5a):
        """
        0x5a = 90
        :type i2c: machine.I2C
        :type addr: int
        """
        prometheus.Prometheus.__init__(self)
        self.ccs811 = CCS811.CCS811(i2c=i2c, addr=addr)

    @prometheus.Registry.register('CCS822', 'v', str)
    def value(self, **kwargs):
        if not self.ccs811.data_ready():
            return None
        return '%d %d' % (self.ccs811.eCO2, self.ccs811.tVOC)
