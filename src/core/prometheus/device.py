# coding=utf-8
import gc
import machine
import prometheus
import prometheus.logging as logging

__version__ = '0.1.2'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()

# TODO: create superclass for ESP8266, ESP32 (with just integrated led), and an esp8266 subclass for the PCB
# further, perhaps create a subclass for the PCB that autodetects devices? got to fix some of those devices too
# undo this code file from GIT to get a better starting point for the superclasses


class Esp8266(prometheus.Prometheus):
    def __init__(self):
        print('esp8266 init')
        prometheus.Prometheus.__init__(self)
        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), inverted=True, state=False)
        self.register(prefix='i', integrated_led=self.integrated_led)


class LanotPcb(object):
    def __init__(self, node, i2c):
        """
        :type node: prometheus.Prometheus
        :type i2c: machine.I2C
        """
        print('lanotpcb init')
        self.node = node
        self.i2c = i2c

        self.ssd = None
        self.ds1307 = None
        self.at24c32 = None
        self.ccs811 = None
        self.ads1115 = None
        self.nano = None
        self.scan_i2c()

        if self.ssd is not None:
            self.ssd.text('init', 0, 0)

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
        elif 0x68 not in scan and self.ds1307 is not None:
            logging.notice('Removed: DS1307 RTC')
            self.ds1307 = None

        # 87 = AT24C32N EEPROM
        if 0x57 in scan and self.at24c32 is None:
            logging.notice('Added: AT24C32 EEPROM')
            import at24c32n
            self.at24c32 = at24c32n.AT24C32N(i2c=self.i2c, i2c_addr=0x57, pages=256, bpp=32)
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
        elif 0x5a not in scan and self.ccs811 is not None:
            logging.notice('Removed: CCS811 gas sensor')
            self.ccs811 = None

        # 72 ads1115 4 channel 12 bit ADC
        if 0x48 in scan and self.ads1115 is None:
            logging.notice('Added: ADS1115 ADC')
            import prometheus.pads1115
            self.ads1115 = prometheus.pads1115.ADS1115(i2c=self.i2c, addr=0x48)
        elif 0x48 not in scan and self.ads1115 is not None:
            logging.notice('Removed: ADS1115 ADC')
            self.ads1115 = None

        # 8 = Nano IO extension
        if 0x8 in scan and self.nano is None:
            logging.notice('Added: Nano')
            import prometheus.pnano
            self.nano = prometheus.pnano.NanoI2C(i2c=self.i2c)
        elif 0x8 not in scan and self.nano is not None:
            logging.notice('Removed: Nano')
            self.nano = None

        gc.collect()


class Esp8266Pcb(Esp8266, LanotPcb):
    def __init__(self):
        print('esp8266pcb init')
        Esp8266.__init__(self)

        self.adc1 = prometheus.Adc(0)
        self.register(prefix='a', adc1=self.adc1)

        LanotPcb.__init__(self, self, machine.I2C(scl=machine.Pin(0), sda=machine.Pin(4), freq=400000))

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
