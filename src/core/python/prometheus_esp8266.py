import dht
import prometheus


# TODO: i suspect this really should be a package under prometheus


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
        self.dht.measure()

    @prometheus.Registry.register('Dht11', 't', 'OUT')
    def temperature(self):
        return self.dht.temperature()

    @prometheus.Registry.register('Dht11', 'h', 'OUT')
    def humidity(self):
        return self.dht.humidity()


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
