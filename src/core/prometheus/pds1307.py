# coding=utf-8
import prometheus
import machine
import ds1307
import gc

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class DS1307(prometheus.Prometheus):
    def __init__(self, i2c, addr=0x68):
        """
        0x68 = 104
        :type i2c: machine.I2C
        :type addr: int
        """
        prometheus.Prometheus.__init__(self)
        self.ds1307 = ds1307.DS1307(i2c=i2c, addr=addr)

    @prometheus.Registry.register('DS1307', 'v', str)
    def value(self, **kwargs):
        dt = self.ds1307.datetime()
        return '%02d:%02d:%02d' % (dt[4], dt[5], dt[6])
