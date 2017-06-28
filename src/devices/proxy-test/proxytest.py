import sys
import random
import prometheus
sys.path.append('P:\lanot\build\clients')
import nodeclient


class ProxyTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
        self.nodeclient = nodeclient.NodeTestUdpClient('192.168.1.188', bind_port=random.randrange(1024, 9000))
        self.register(prefix='nc', nodeclient=self.nodeclient)

if __name__ == '__main__':
    proxytest = ProxyTest()
    proxytest.nodeclient.blue_led.on()
    udpserver = prometheus.UdpSocketServer(proxytest)
