import prometheus
import prometheus_esp8266
import machine
import gc


gc.collect()


class Test01(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), state=False)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.laser = prometheus.Led(machine.Pin(0, machine.Pin.OUT), state=False)
        self.register(prefix='l', laser=self.laser)

        self.lightsensor = prometheus.Adc(machine.Pin(36))
        self.register(prefix='s', lightsensor=self.lightsensor)

        self.window01digital = prometheus.Digital(machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP))
        self.register(prefix='w1', window01digital=self.window01digital)

        self.window02digital = prometheus.Digital(machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP))
        self.register(prefix='w2', window02digital=self.window02digital)
