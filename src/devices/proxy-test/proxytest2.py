import sys
import random
import prometheus
import prometheus_servers
import time
sys.path.append('P:\lanot\build\clients')
import sensor01client
import sensor02client
import nodetestclient


class ProxyTest2(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.sensor01 = sensor01client.Sensor01UdpClient('sensor01', bind_port=random.randrange(1024, 9000))
        self.register(prefix='s1', sensor01=self.sensor01)

        self.sensor02 = sensor02client.Sensor02UdpClient('sensor02', bind_port=random.randrange(1024, 9000))
        self.register(prefix='s2', sensor02=self.sensor02)

        self.nodetest = nodetestclient.NodeTestUdpClient('nodetest', bind_port=random.randrange(1024, 9000))
        self.register(prefix='nt', nodetest=self.nodetest)


if __name__ == '__main__':
    proxytest2 = ProxyTest2()
    # print('off')
    # proxytest2.sensor01.integrated_led.off()
    # proxytest2.sensor02.integrated_led.off()
    # proxytest2.nodetest.integrated_led.off()
    # time.sleep(2)
    # print('on')
    # proxytest2.sensor01.integrated_led.on()
    # proxytest2.sensor02.integrated_led.on()
    # proxytest2.nodetest.integrated_led.on()
    jsonrestserver = prometheus_servers.JsonRestServer(proxytest2)
    jsonrestserver.start()
