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

        self.lightsensor = prometheus.Adc(machine.Pin(36, machine.Pin.IN))
        self.register(prefix='s', lightsensor=self.lightsensor)

        self.red_led = prometheus.Led(machine.Pin(19, machine.Pin.OUT), state=False)
        self.register(prefix='r', red_led=self.red_led)

        self.yellow_led = prometheus.Led(machine.Pin(18, machine.Pin.OUT), state=False)
        self.register(prefix='y', yellow_led=self.yellow_led)

        self.green_led = prometheus.Led(machine.Pin(5, machine.Pin.OUT), state=False)
        self.register(prefix='g', green_led=self.green_led)

        self.blue_led = prometheus.Led(machine.Pin(17, machine.Pin.OUT, machine.Pin.PULL_DOWN), state=False)
        self.register(prefix='b', blue_led=self.blue_led)

        self.uw_led = prometheus.Led(machine.Pin(16, machine.Pin.OUT, machine.Pin.PULL_DOWN), state=False)
        self.register(prefix='u', uw_led=self.uw_led)
