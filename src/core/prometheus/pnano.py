# coding=utf-8
import prometheus
import time
import gc

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class NanoI2C(prometheus.Prometheus):
    def __init__(self, i2c):
        prometheus.Prometheus.__init__(self)
        self.i2c = i2c

    @prometheus.Registry.register('NanoI2C', 'do')
    def digital_out(self, pin=4, value=1, **kwargs):
        # if not pin in range(0,12):
        self.i2c.writeto(8, b'DO %d %d' % (pin, value))

    @prometheus.Registry.register('NanoI2C', 'di', bool)
    def digital_in(self, pin=4, **kwargs):
        if pin not in range(0, 12):
            raise Exception("Invalid pin")
        self.i2c.writeto(8, b'DI %d' % pin)
        # 0=rx, 1=tx, 4=sda, 5=scl (should not be used)
        time.sleep(0.2)
        i2cdata = self.i2c.readfrom(8, 1)
        # print(data)
        return i2cdata == b'\x01'

    def _infrain_getdata(self):
        i2cdata = self.i2c.readfrom(8, 9)
        # print(i2cdata)
        i2cdata = i2cdata.split(b' ')
        if len(i2cdata) == 3:
            return i2cdata[0], i2cdata[1], i2cdata[2]
        else:
            return None, None, None

    @prometheus.Registry.register('NanoI2C', 'ii', str)
    def infrain(self, **kwargs):
        _type, code, bitlength = self._infrain_getdata()
        if _type is not None:
            return '%s %s %s' % (_type, code, bitlength)

        self.i2c.writeto(8, b'RECV')
        time.sleep(0.2)
        _type, code, bitlength = self._infrain_getdata()
        return '%s %s %s' % (_type, code, bitlength)

    @prometheus.Registry.register('NanoI2C', 'io')
    def infraout(self, device, code, bitlength, **kwargs):
        self.i2c.writeto(8, b'%s %x %d' % (device, code, bitlength))
