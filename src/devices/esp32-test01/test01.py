import prometheus
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

        self.window01digital = prometheus.Digital(machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP))
        self.register(prefix='w1', window01digital=self.window01digital)

        self.window02digital = prometheus.Digital(machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP))
        self.register(prefix='w2', window02digital=self.window02digital)

        self.joystickx = prometheus.Adc(machine.Pin(36, machine.Pin.IN))
        self.register(prefix='x', joystickx=self.joystickx)
        self.joystickx.adc.width(machine.ADC.WIDTH_12BIT)
        self.joystickx.adc.atten(machine.ADC.ATTN_11DB)

        self.joysticky = prometheus.Adc(machine.Pin(39, machine.Pin.IN))
        self.register(prefix='y', joysticky=self.joysticky)
        self.joysticky.adc.width(machine.ADC.WIDTH_12BIT)
        self.joysticky.adc.atten(machine.ADC.ATTN_11DB)

        self.joystickswitch = prometheus.Digital(machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_UP))
        self.register(prefix='j', joystickswitch=self.joystickswitch)

        self.switch = prometheus.Digital(machine.Pin(35, machine.Pin.IN))
        self.register(prefix='s', switch=self.switch)
