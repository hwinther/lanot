# coding=utf-8
import prometheus
import dht
import gc

__version__ = '0.1.2b'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class Dht22(prometheus.Prometheus):
    def __init__(self, pin):
        """
        :type pin: machine.Pin
        """
        prometheus.Prometheus.__init__(self)
        self.pin = pin
        self.dht = dht.DHT22(self.pin)

    @prometheus.Registry.register('Dht22', 'm')
    def measure(self):
        try:
            self.dht.measure()
        except OSError:
            pass

    @prometheus.Registry.register('Dht22', 't', 'OUT')
    def temperature(self):
        self.dht.temperature()

    @prometheus.Registry.register('Dht22', 'h', 'OUT')
    def humidity(self):
        return self.dht.humidity()

    @prometheus.Registry.register('Dht22', 'v', 'OUT')
    def value(self):
        try:
            self.dht.measure()
        except OSError:
            return 'timeout'
        return '%sc%s' % (self.dht.temperature(), self.dht.humidity())
