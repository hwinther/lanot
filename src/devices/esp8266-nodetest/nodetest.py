import gc
import machine
import onewire
import prometheus
import prometheus.dht11
import prometheus.pds18x20
import prometheus.pneopixel
import prometheus.pssd1306
import prometheus.pmax7219
import prometheus.pccs822
import prometheus.pds1307
import prometheus.pads1115
import prometheus.pnano
import prometheus.logging as logging

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

        # endregion

        # region lanot pcb-01b feaures

        self.i2c = machine.I2C(scl=machine.Pin(0), sda=machine.Pin(4), freq=400000)
        logging.info('i2c: %s' % self.i2c.scan())

        self.spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0)

        self.neopixel = prometheus.pneopixel.NeoPixel(machine.Pin(2), 256)
        self.register(prefix='p', neopixel=self.neopixel)

        # region i2c devices

        self.ssd = prometheus.pssd1306.SSD1306(self.i2c)
        self.register(prefix='ss', ssd=self.ssd)

        self.max = prometheus.pmax7219.MAX7219(self.spi, machine.Pin(15), 4)
        self.register(prefix='ma', max=self.max)

        self.ds1307 = prometheus.pds1307.DS1307(self.i2c)
        self.register(prefix='ds', ds1307=self.ds1307)

        self.ads = prometheus.pads1115.ADS1115(self.i2c)
        self.register(prefix='ad', ads=self.ads)

        self.nano = prometheus.pnano.NanoI2C(self.i2c)
        self.register(prefix='na', nano=self.nano)

        # endregion

        if prometheus.is_micro:
            self.ssd.text('init', 0, 0)
            self.max.text('init', 0, 0, 1)
            # write empty to clear potentially enabled pixels
            self.neopixel.write()

        # endregion
