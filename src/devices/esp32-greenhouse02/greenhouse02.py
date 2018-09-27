import machine
import gc
# import ssd1306
import prometheus
import prometheus.pssd1306

gc.collect()


class Greenhouse02(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), state=False)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.hygrometer01 = prometheus.Adc(machine.Pin(36, machine.Pin.IN))
        self.register(prefix='h1', hygrometer01=self.hygrometer01)
        self.hygrometer01.adc.width(machine.ADC.WIDTH_12BIT)
        self.hygrometer01.adc.atten(machine.ADC.ATTN_11DB)

        self.hygrometer02 = prometheus.Adc(machine.Pin(39, machine.Pin.IN))
        self.register(prefix='h2', hygrometer02=self.hygrometer02)
        self.hygrometer02.adc.width(machine.ADC.WIDTH_12BIT)
        self.hygrometer02.adc.atten(machine.ADC.ATTN_11DB)

        self.hygrometer03 = prometheus.Adc(machine.Pin(34, machine.Pin.IN))
        self.register(prefix='h3', hygrometer03=self.hygrometer03)
        self.hygrometer03.adc.width(machine.ADC.WIDTH_12BIT)
        self.hygrometer03.adc.atten(machine.ADC.ATTN_11DB)

        self.hygrometer04 = prometheus.Adc(machine.Pin(35, machine.Pin.IN))
        self.register(prefix='h4', hygrometer04=self.hygrometer04)
        self.hygrometer04.adc.width(machine.ADC.WIDTH_12BIT)
        self.hygrometer04.adc.atten(machine.ADC.ATTN_11DB)

        self.i2c = machine.I2C(freq=400000, scl=machine.Pin(22, machine.Pin.OUT), sda=machine.Pin(21, machine.Pin.OUT))

        self.ssd = prometheus.pssd1306.SSD1306(width=128, height=64, i2c=self.i2c)
        self.register(prefix='ss', ssd=self.ssd)

        self.ssd.text('init', 0, 0)
