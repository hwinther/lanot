import time
import gc

gc.collect()


class NanoI2C(object):
    def __init__(self, i2c):
        self.i2c = i2c

    def digital_out(self, pin, value):
        # if not pin in range(0,12):
        self.i2c.writeto(8, b'DO %d %d' %(pin, value))

    def digital_in(self, pin):
        if pin not in range(0,12):
            raise Exception("Invalid pin")
        self.i2c.writeto(8, b'DI %d' % pin)
        # 0=rx, 1=tx, 4=sda, 5=scl (should not be used)
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

    def infrain(self):
        type, code, bitlength = self._infrain_getdata()
        if type is not None:
            return type, code, bitlength

        self.i2c.writeto(8, b'RECV')
        time.sleep(0.2)
        type, code, bitlength = self._infrain_getdata()
        return type, code, bitlength

    def infraout(self, type, code, bitlength):
        self.i2c.writeto(8, b'%s %x %d' %(type, code, bitlength))
