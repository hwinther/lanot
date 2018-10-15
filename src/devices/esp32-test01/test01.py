import prometheus
import prometheus.logging as logging
import ssd1306
import machine
import gc

gc.collect()


class Test01(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), state=False)
        self.register(prefix='i', integrated_led=self.integrated_led)

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

        self.switch1 = prometheus.Digital(machine.Pin(35, machine.Pin.IN))
        self.register(prefix='s1', switch1=self.switch1)

        self.switch2 = prometheus.Digital(machine.Pin(32, machine.Pin.IN))
        self.register(prefix='s2', switch2=self.switch2)

        self.switch3 = prometheus.Digital(machine.Pin(33, machine.Pin.IN))
        self.register(prefix='s3', switch3=self.switch3)

        self.i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21), freq=400000)
        logging.info('i2c: %s' % self.i2c.scan())

        self.ssd = ssd1306.SSD1306_I2C(width=128, height=64, i2c=self.i2c)
        self.register(prefix='ss', ssd=self.ssd)

        self.ssd.fill(False)
        self.ssd.text('init', 0, 0)
        self.ssd.show()
