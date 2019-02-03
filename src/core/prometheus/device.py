# coding=utf-8
import gc
import machine
import onewire
import prometheus
import prometheus.logging as logging

__version__ = '0.1.4'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()

# TODO: create superclass for ESP8266, ESP32 (with just integrated led), and an esp8266 subclass for the PCB
# further, perhaps create a subclass for the PCB that autodetects devices? got to fix some of those devices too
# undo this code file from GIT to get a better starting point for the superclasses


class Esp8266(prometheus.Prometheus):
    def __init__(self):
        # print('esp8266 init')
        prometheus.Prometheus.__init__(self)
        # self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), inverted=True, state=False)
        # self.register(prefix='i', integrated_led=self.integrated_led)


class LanotPcb(object):
    def __init__(self, node, i2c, ow, dhtpin, spi, enable_spi_max7219=False, neopixel_pin=None, neopixel_amount=None):
        """
        :type node: prometheus.Prometheus
        :type i2c: machine.I2C
        """
        # print('lanotpcb init')
        self.node = node
        self.i2c = i2c
        self.ow = ow
        self.dhtpin = dhtpin

        self.ssd = None
        self.ds1307 = None
        self.at24c32 = None
        self.ccs811 = None
        self.ads1115 = None
        self.nano = None
        self.bmp280 = None
        self.hdc1080 = None

        if i2c is not None:
            self.scan_i2c()

        self.ds18 = None
        if self.ow is not None:
            self.scan_onewire()

        self.dht = None
        if self.dhtpin is not None:
            self.scan_dht()

        self.spi = spi

        self.max7219 = None
        if spi is not None and enable_spi_max7219:
            import prometheus.pmax7219
            self.max7219 = prometheus.pmax7219.MAX7219(self.spi, machine.Pin(15), 4)
            self.node.register(prefix='ma', max=self.max7219)
            gc.collect()

        self.neopixel = None
        if neopixel_pin is not None:
            import prometheus.pneopixel
            logging.notice('Added %d neopixels' % neopixel_amount)
            self.neopixel = prometheus.pneopixel.NeoPixel(neopixel_pin, neopixel_amount)
            self.node.register(prefix='p', neopixel=self.neopixel)
            gc.collect()

        if self.ssd is not None:
            self.ssd.text('init', 0, 0)
        if self.max7219 is not None:
            self.max7219.text('init', 0, 0)

    def scan_i2c(self):
        """
        Scan for devices on the I2C bus, remove previously detected devices if they are gone (set back to None)
        """
        scan = self.i2c.scan()
        logging.debug('i2c: %s' % scan)

        # 60 = SSD OLED display
        if 0x3c in scan and self.ssd is None:
            logging.notice('Added: SSD1306 OLED display')
            import prometheus.pssd1306
            self.ssd = prometheus.pssd1306.SSD1306(i2c=self.i2c, addr=0x3c, width=128, height=64)
            self.node.register(prefix='ss', ssd=self.ssd)
        elif 0x3c not in scan and self.ssd is not None:
            logging.notice('Removed: SSD1306 display')
            self.ssd = None

        # 104 = DS1307 rtc
        if 0x68 in scan and self.ds1307 is None:
            logging.notice('Added: DS1307 RTC')
            import prometheus.pds1307
            self.ds1307 = prometheus.pds1307.DS1307(self.i2c, 0x68)
            self.node.register(prefix='ds', ds1307=self.ds1307)
        elif 0x68 not in scan and self.ds1307 is not None:
            logging.notice('Removed: DS1307 RTC')
            self.ds1307 = None

        # 87 = AT24C32N EEPROM
        if 0x57 in scan and self.at24c32 is None:
            logging.notice('Added: AT24C32 EEPROM')
            import at24c32n
            self.at24c32 = at24c32n.AT24C32N(i2c=self.i2c, i2c_addr=0x57, pages=256, bpp=32)
            # TODO: create prometheus wrapper for this device?
        elif 0x57 not in scan and self.at24c32 is not None:
            logging.notice('Removed: AT24C32 EEPROM')
            self.at24c32 = None

        # 90 = CCS811 gas sensor
        if 0x5a in scan and self.ccs811 is None:
            logging.notice('Added: CCS811 gas sensor')
            import prometheus.pccs822
            # time.sleep(0.5)
            # fix with the skew setting Tor mentioned?
            self.ccs811 = prometheus.pccs822.Ccs811(i2c=self.i2c, addr=90)
            self.node.register(prefix='cc', ads=self.ccs811)
        elif 0x5a not in scan and self.ccs811 is not None:
            logging.notice('Removed: CCS811 gas sensor')
            self.ccs811 = None

        # 72 ads1115 4 channel 12 bit ADC
        if 0x48 in scan and self.ads1115 is None:
            logging.notice('Added: ADS1115 ADC')
            import prometheus.pads1115
            self.ads1115 = prometheus.pads1115.ADS1115(i2c=self.i2c, addr=0x48)
            self.node.register(prefix='ad', ads=self.ads1115)
        elif 0x48 not in scan and self.ads1115 is not None:
            logging.notice('Removed: ADS1115 ADC')
            self.ads1115 = None

        # 8 = Nano IO extension
        if 0x8 in scan and self.nano is None:
            logging.notice('Added: Nano')
            import prometheus.pnano
            self.nano = prometheus.pnano.NanoI2C(i2c=self.i2c)
            self.node.register(prefix='na', nano=self.nano)
        elif 0x8 not in scan and self.nano is not None:
            logging.notice('Removed: Nano')
            self.nano = None

        # 118  = BMP280 temperature, altitude and pressure sensor
        if 0x76 in scan and self.bmp280 is None:
            logging.notice('Added: BMP280')
            import prometheus.pbmp280
            self.bmp280 = prometheus.pbmp280.Bmp280(i2c=self.i2c)
            self.node.register(prefix='bm', nano=self.bmp280)
        elif 0x76 not in scan and self.bmp280 is not None:
            logging.notice('Removed: BMP280')
            self.bmp280 = None

        # 64 = HDC1080 humidity and temperature sensor
        if 0x40 in scan and self.hdc1080 is None:
            logging.notice('Added: HDC1080')
            import prometheus.phdc1080
            self.hdc1080 = prometheus.phdc1080.Hdc1080(i2c=self.i2c)
            self.node.register(prefix='hd', nano=self.hdc1080)
        elif 0x40 not in scan and self.hdc1080 is not None:
            logging.notice('Removed: HDC1080')
            self.hdc1080 = None

        gc.collect()

    def scan_onewire(self):
        ow_scan = self.ow.scan()
        # TODO: also deal with the amount of/specific ds18 devices changing
        if len(ow_scan) != 0 and self.ds18 is None:
            logging.notice('Added: %d onewire device(s): %s' % (len(ow_scan), ow_scan))
            import prometheus.pds18x20
            self.ds18 = prometheus.pds18x20.Ds18x20(ow=self.ow)
            self.node.register(prefix='s', dsb=self.ds18)
        elif len(ow_scan) == 0 and self.ds18 is not None:
            logging.notice('Removed: onewire device(s)')
            self.ds18 = None
        gc.collect()

    def scan_dht(self):
        # check if dht is connected
        import prometheus.dht11
        gc.collect()
        # TODO: deal with DHT already existing (now we can create a second one on rescan)
        dht = prometheus.dht11.Dht11(self.dhtpin)
        try:
            dht.dht.measure()
            logging.notice('Added: DHT11')
            self.dht = dht
            self.node.register(prefix='d', dht11=self.dht)
        except OSError:
            if self.dht is not None:
                logging.notice('Removed: DHT11')
                self.dht = None


class Esp8266Pcb(Esp8266, LanotPcb):
    def __init__(self, enable_i2c=False, enable_onewire=False, enable_dht=False, enable_spi=False,
                 enable_spi_max7219=False, neopixel_amount=None, neopixel_pin=None):
        # print('esp8266pcb init')
        Esp8266.__init__(self)

        self.adc1 = prometheus.Adc(0)
        self.register(prefix='a', adc1=self.adc1)

        i2c = machine.I2C(scl=machine.Pin(0), sda=machine.Pin(4), freq=400000) if enable_i2c else None
        ow = onewire.OneWire(machine.Pin(5, machine.Pin.IN)) if enable_onewire else None
        dhtpin = machine.Pin(12, machine.Pin.OUT) if enable_dht else None
        spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0) if enable_spi else None
        np_pin = 2 if neopixel_pin is None else neopixel_pin
        neopixel_pin = machine.Pin(np_pin) if neopixel_amount is not None else None

        LanotPcb.__init__(self, node=self, i2c=i2c, ow=ow, dhtpin=dhtpin, spi=spi,
                          enable_spi_max7219=enable_spi_max7219,
                          neopixel_pin=neopixel_pin, neopixel_amount=neopixel_amount)

    @prometheus.Registry.register('Esp8266Pcb', 'rs')
    def rescan(self):
        # TODO: perhaps see if this could be registered via LanotPcb (does not work at present)
        logging.info("Rescanning I2C")
        self.scan_i2c()

    def custom_command(self, command, reply, source, context, **kwargs):
        # ret = Esp8266Pcb.custom_command(self, command, reply, source, context, **kwargs)
        # if ret is True:
        #     return True

        if command == 'rescan':
            logging.info("Rescanning I2C")
            self.scan_i2c()
            return True

        return False
