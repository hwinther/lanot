import prometheus
import prometheus.logging as logging
import onewire
import ds18x20
import time
import gc

__version__ = '0.1.2b'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class Ds18x20(prometheus.Prometheus):
    def __init__(self, pin):
        """
        :type pin: machine.Pin
        """
        prometheus.Prometheus.__init__(self)
        self.pin = pin
        self.ds = ds18x20.DS18X20(onewire.OneWire(pin))
        self.roms = list()
        self.scan()

    def scan(self):
        try:
            self.roms = self.ds.scan()
        except onewire.OneWireError:
            self.roms = list()
        logging.notice('found devices: %s' % self.roms)

    @prometheus.Registry.register('Ds18x20', 'v', 'OUT')
    def value(self):
        self.ds.convert_temp()
        time.sleep_ms(750)
        temps = list()
        for rom in self.roms:
            try:
                temps.append(self.ds.read_temp(rom))
            except onewire.OneWireError:
                pass
        lt = len(temps)
        if lt == 0:
            return 'timeout'
        elif lt == 1:
            return '%.4f' % temps[0]
        else:
            return ','.join(['%.4f' % x for x in temps])
