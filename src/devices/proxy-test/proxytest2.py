import sys
import random
import prometheus
import prometheus_servers
import time
sys.path.append('P:\lanot\build\clients')
import sensor01client
import sensor02client
import nodetestclient
import tankclient


class ProxyTest2(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.sensor01 = sensor01client.Sensor01UdpClient('sensor01', bind_port=random.randrange(1024, 9000))
        self.register(prefix='s1', sensor01=self.sensor01)

        self.sensor02 = sensor02client.Sensor02UdpClient('sensor02', bind_port=random.randrange(1024, 9000))
        self.register(prefix='s2', sensor02=self.sensor02)

        #self.nodetest = nodetestclient.NodeTestRsaUdpClient('nodetest', bind_port=random.randrange(1024, 9000))
        #self.register(prefix='nt', nodetest=self.nodetest)

        #self.tankclient = tankclient.TankUdpClient('192.168.1.250', bind_port=random.randrange(1024, 9000))
        #self.register(prefix='tc', tankclient=self.tankclient)


if __name__ == '__main__':
    proxytest2 = ProxyTest2()
    print('off')
    proxytest2.sensor01.integrated_led.off()
    proxytest2.sensor02.integrated_led.off()
    # proxytest2.nodetest.integrated_led.off()
    # proxytest2.tankclient.lightControl.all_on()
    time.sleep(2)
    print('on')
    proxytest2.sensor01.integrated_led.on()
    proxytest2.sensor02.integrated_led.on()
    # proxytest2.nodetest.integrated_led.on()
    # proxytest2.tankclient.lightControl.all_off()
    jsonrestserver = prometheus_servers.JsonRestServer(proxytest2, settimeout=0.1)  # , usessl=True)
    jsonrestserver.start()

    # time.struct_time(tm_year=2017, tm_mon=9, tm_mday=3, tm_hour=1, tm_min=22, tm_sec
    # =54, tm_wday=6, tm_yday=246, tm_isdst=1)
    # lt = time.localtime()
    #
    # yd = 2016 - lt[0] * 365 * 24 * 60 * 60
    # et = yd
    # md = lt[1] * 24 * 60 * 60
    # et = et + md
    # dd = lt[2] * 60 * 60
    # et = et + dd
    # hd = lt[3] * 60
    # et = et + hd
    # et = et + lt[4]