# coding=utf-8
import machine
import ds1307
import gc
import prometheus
import prometheus.logging as logging

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class DS1307(prometheus.Prometheus):
    def __init__(self, i2c, addr=0x68):
        """
        0x68 = 104
        value:
        (2000, 1, 11, 3, 0, 11, 58, 0)
        year, mo,day, wd,hr,min,sec, ss
        UTC: 2018-09-28T18:33:35Z
        :type i2c: machine.I2C
        :type addr: int
        """
        prometheus.Prometheus.__init__(self)
        self.ds1307 = ds1307.DS1307(i2c=i2c, addr=addr)

    @prometheus.Registry.register('DS1307', 'v', str)
    def value(self, value=None, **kwargs):
        if value is not None and value.find('T') != -1 and value.find('Z') != -1:
            # ISO datetime parsing on the cheap
            dt = list()
            date, time = value.split('T', 1)
            time = time.replace('Z', '')
            date = date.split('-')
            time = time.split(':')
            if len(date) == 3 and len(time) == 3:
                dt.append(int(date[0]))
                dt.append(int(date[1]))
                dt.append(int(date[2]))
                dt.append(0)  # weekday
                dt.append(int(time[0]))
                dt.append(int(time[1]))
                dt.append(int(time[2]))
                dt.append(0)  # milli
            logging.info('setting RTC with: %s' % repr(dt))
            # logging.debug('date=%s time=%s' % (date, time))
            # logging.debug('dt[0]=%d dt[1]=%d dt[2]=%d' % (dt[0], dt[1], dt[2]))
            # logging.debug('dt[4]=%d dt[5]=%d dt[6]=%d' % (dt[4], dt[5], dt[6]))
            self.ds1307.datetime(dt)

        dt = self.ds1307.datetime()
        return '%d-%d-%dT%02d:%02d:%02dZ' % (dt[0], dt[1], dt[2], dt[4], dt[5], dt[6])
