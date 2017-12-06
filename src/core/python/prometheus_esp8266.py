import prometheus
import prometheus_logging as logging
import dht
import onewire
import ds18x20
import time
import gc

__version__ = '0.1.2a'
__author__ = 'Hans Christian Winther-Sorensen'

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
    def measure(self):
        try:
            self.dht.measure()
        except OSError:
            pass

    @prometheus.Registry.register('Dht11', 't', 'OUT')
    def temperature(self):
        return self.dht.temperature()

    @prometheus.Registry.register('Dht11', 'h', 'OUT')
    def humidity(self):
        return self.dht.humidity()

    @prometheus.Registry.register('Dht11', 'v', 'OUT')
    def value(self):
        try:
            self.dht.measure()
        except OSError:
            return 'timeout'
        return '%sc%s' % (self.dht.temperature(), self.dht.humidity())


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
        self.dht.measure()

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


class Ds18x20(prometheus.Prometheus):
    def __init__(self, pin):
        """
        :type pin: machine.Pin
        """
        prometheus.Prometheus.__init__(self)
        self.pin = pin
        self.ds = ds18x20.DS18X20(onewire.OneWire(pin))
        self.roms = list()
        self.scan()

    def scan(self):
        try:
            self.roms = self.ds.scan()
        except onewire.OneWireError:
            self.roms = list()
        logging.notice('found devices: %s' % self.roms)

    @prometheus.Registry.register('Ds18x20', 'v', 'OUT')
    def value(self):
        self.ds.convert_temp()
        time.sleep_ms(750)
        temps = list()
        for rom in self.roms:
            try:
                temps.append(self.ds.read_temp(rom))
            except onewire.OneWireError:
                pass
        lt = len(temps)
        if lt == 0:
            return 'timeout'
        elif lt == 1:
            return '%.4f' % temps[0]
        else:
            return ','.join(['%.4f' % x for x in temps])
