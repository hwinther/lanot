# coding=utf-8
import prometheus
import dht
import gc

__version__ = '0.1.2b'
__author__ = 'Hans Christian Winther-Sorensen'
# TODO: merge dht11 with dht22 via inheritance

gc.collect()


class Dht11(prometheus.Prometheus):
    def __init__(self, pin):
        """
        :type pin: machine.Pin
        """
        prometheus.Prometheus.__init__(self)
        self.pin = pin
        self.dht = dht.DHT11(self.pin)

    @prometheus.Registry.register('Dht11', 'm')
    def measure(self, **kwargs):
        try:
            self.dht.measure()
        except OSError:
            pass

    @prometheus.Registry.register('Dht11', 't', str)
    def temperature(self, **kwargs):
        return self.dht.temperature()

    @prometheus.Registry.register('Dht11', 'h', str)
    def humidity(self, **kwargs):
        return self.dht.humidity()

    @prometheus.Registry.register('Dht11', 'v', str)
    def value(self, **kwargs):
        try:
            self.dht.measure()
        except OSError:
            return 'timeout'
        return '%sc%s' % (self.dht.temperature(), self.dht.humidity())
