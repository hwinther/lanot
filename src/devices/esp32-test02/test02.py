import prometheus
import machine
import gc


gc.collect()


class Test02(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), state=False)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.door_sensor = prometheus.Digital(machine.Pin(32, machine.Pin.IN, machine.Pin.PULL_DOWN))
        self.register(prefix='d', door_sensor=self.door_sensor)

        self.infrared_sensor = prometheus.Digital(machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_DOWN))
        self.register(prefix='s', infrared_sensor=self.infrared_sensor)

        self.light_switch = prometheus.Digital(machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_DOWN))
        self.register(prefix='l', light_switch=self.light_switch)
