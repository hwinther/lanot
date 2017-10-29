import prometheus
import prometheus_esp8266
import machine
import gc


gc.collect()


class Test02(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), state=False)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.lightsensor = prometheus.Adc(machine.Pin(36))
        self.register(prefix='s', lightsensor=self.lightsensor)
