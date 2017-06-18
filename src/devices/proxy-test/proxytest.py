import sys
import random
import prometheus
sys.path.append('P:\lanot\build\clients')
import nodeclient


class ProxyTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
        self.nodeclient = nodeclient.NodeTestUdp('192.168.1.188', local_port=random.randrange(1024, 9000))
        self.register(nodeclient=self.nodeclient)

if __name__ == '__main__':
    proxytest = ProxyTest()
    proxytest.nodeclient.blue_led.on()
    proxytest.start_socket_server()
