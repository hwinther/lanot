import gc
import machine
import ssd1306
import onewire
import max7219
import prometheus
import prometheus.dht11
import prometheus.pds18x20

gc.collect()


class NodeTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        # region ESP8266 defaults:

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), inverted=True)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.dht11 = prometheus.dht11.Dht11(machine.Pin(12, machine.Pin.OUT))
        self.register(prefix='d', dht11=self.dht11)

        self.onewire = onewire.OneWire(machine.Pin(5, machine.Pin.IN))
        self.dsb = prometheus.pds18x20.Ds18x20(ow=self.onewire)
        self.register(prefix='s', dsb=self.dsb)

        self.adc1 = prometheus.Adc(0)
        self.register(prefix='a', adc1=self.adc1)

        self.i2c = machine.I2C(freq=400000, scl=machine.Pin(0, machine.Pin.OUT), sda=machine.Pin(4, machine.Pin.OUT))
        self.ssd = ssd1306.SSD1306_I2C(width=128, height=64, i2c=self.i2c)

        self.spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0)
        self.display = max7219.Matrix8x8(self.spi, machine.Pin(15), 4)

        # endregion

        self.green_led = prometheus.Led(machine.Pin(16, machine.Pin.OUT))
        self.register(prefix='g', blue_led=self.green_led)

        if prometheus.is_micro:
            self.ssd.fill(False)
            self.ssd.text('init', 0, 0)
            self.ssd.show()

            self.display.brightness(0)
            self.display.fill(False)
            self.display.text('init', 0, 0, 1)
            self.display.show()

    def custom_command(self, command, reply, source, **kwargs):
        print('custom cmd: %s' % command)

        if len(command) > 6 and command[0:6] == 'stext ':
            self.ssd.fill(False)
            self.ssd.text(command[6:], 0, 0)
            self.ssd.show()
            gc.collect()
            return True
        elif len(command) > 6 and command[0:6] == 'dtext ':
            self.display.fill(False)
            self.display.text(command[6:], 0, 0, 1)
            self.display.show()
            gc.collect()
            return True

        return prometheus.Prometheus.custom_command(self, command, reply, source, **kwargs)
