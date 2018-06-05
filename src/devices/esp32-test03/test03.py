import prometheus
import machine
import gc
import ssd1306

gc.collect()


class Test03(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), state=False)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.i2c = machine.I2C(freq=400000, scl=machine.Pin(22, machine.Pin.OUT), sda=machine.Pin(21, machine.Pin.OUT))
        self.ssd = ssd1306.SSD1306_I2C(width=128, height=64, i2c=self.i2c)

        self.ssd.fill(False)
        self.ssd.text('init', 0, 0)
        self.ssd.show()
