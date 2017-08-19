import prometheus
import prometheus_esp8266
import prometheus_servers
import machine


class NodeTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.blue_led = prometheus.Led(machine.Pin(14, machine.Pin.OUT))
        self.register(prefix='b', blue_led=self.blue_led)

        self.red_led = prometheus.Led(machine.Pin(15, machine.Pin.OUT))
        self.register(prefix='r', red_led=self.red_led)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), inverted=True)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.dht11 = prometheus_esp8266.Dht11(machine.Pin(13, machine.Pin.OUT))
        self.register(prefix='d', dht11=self.dht11)

        self.hygrometer = prometheus.Adc(0)
        self.register(prefix='h', hygrometer=self.hygrometer)
