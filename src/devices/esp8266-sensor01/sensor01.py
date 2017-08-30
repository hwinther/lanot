import prometheus
import prometheus_esp8266
import machine
import gc


gc.collect()


class Sensor01(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.dht11 = prometheus_esp8266.Dht11(machine.Pin(13, machine.Pin.OUT))
        self.register(prefix='d', dht11=self.dht11)

        self.lightsensor = prometheus.Adc(0)
        self.register(prefix='l', lightsensor=self.lightsensor)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), inverted=True, state=True)
        self.register(prefix='i', integrated_led=self.integrated_led)
