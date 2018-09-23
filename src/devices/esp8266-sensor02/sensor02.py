import prometheus
import prometheus.dht11
import prometheus.pds18x20
import machine
import gc

gc.collect()


class Sensor02(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), inverted=True)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.dht11 = prometheus.dht11.Dht11(machine.Pin(12, machine.Pin.OUT))
        self.register(prefix='d', dht11=self.dht11)

        self.lightsensor = prometheus.Adc(0)
        self.register(prefix='l', lightsensor=self.lightsensor)

        self.dsb = prometheus.pds18x20.Ds18x20(machine.Pin(5, machine.Pin.IN))
        self.register(prefix='b', dsb=self.dsb)
