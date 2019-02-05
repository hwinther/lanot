# coding=utf-8
import time
import gc
import machine
import prometheus
import prometheus.device
import prometheus.server

gc.collect()


class LocalEvents(prometheus.server.Server):
    def __init__(self, instance):
        """
        :type instance: greenhouse01.GreenHouse01
        """
        prometheus.server.Server.__init__(self, instance)
        self.timer = 0

    def pre_loop(self, **kwargs):
        prometheus.server.Server.pre_loop(self)

        self.timer = time.time() - 300
        self.instance.ssd.ssd.fill(False)
        self.instance.ssd.ssd.text('v: %s' % self.version(), 0, 0)
        self.instance.ssd.ssd.show()

    def loop_tick(self, **kwargs):
        prometheus.server.Server.loop_tick(self)

        diff = time.time() - self.timer
        if diff >= 300:
            self.timer = time.time()
            # print('1 sec event, diff=%d' % diff)
            assert isinstance(self.instance, prometheus.device.LanotPcb)

            if self.instance.ssd is None:
                print('no ssd')
                # ハンス　です
                return

            self.instance.ssd.ssd.fill(0)

            if self.instance.ccs811 is not None and self.instance.ccs811.ccs811.data_ready():
                self.instance.ssd.ssd.text('eCO2 ppm ' + str(self.instance.ccs811.ccs811.eCO2), 0, 0)
                self.instance.ssd.ssd.text('TVOC ppb ' + str(self.instance.ccs811.ccs811.tVOC), 0, 10)

            if self.instance.bmp280 is not None:
                self.instance.ssd.ssd.text('temp ' + str(self.instance.bmp280.bmp280.getTemp()), 0, 20)
                self.instance.ssd.ssd.text('pres ' + str(self.instance.bmp280.bmp280.getPress()), 0, 30)
                self.instance.ssd.ssd.text('alt ' + str(self.instance.bmp280.bmp280.getAltitude()), 0, 40)

            if self.instance.ds1307 is not None:
                da = self.instance.ds1307.ds1307.datetime()
                self.instance.ssd.ssd.text('%02d:%02d:%02d  ' % (da[4], da[5], da[6]), 0, 40)

            if self.instance.dht is not None:
                self.instance.dht.dht.measure()
                self.instance.ssd.ssd.text('%dC %d%%' % (self.instance.dht.dht.temperature(),
                                                         self.instance.dht.dht.humidity()), 0, 50)

            if self.instance.ds18 is not None:
                self.instance.ssd.ssd.text('%s' % self.instance.ds18.value(), 60, 50)

            self.instance.ssd.ssd.show()
            time.sleep(1)
            machine.idle()
