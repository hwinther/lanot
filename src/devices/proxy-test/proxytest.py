import sys
import random
import prometheus
import prometheus.server.socketserver.udp
sys.path.append('P:\lanot\build\clients')
import deploy.clients.nodetestclient


class ProxyTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
        self.nodeclient = deploy.clients.nodetestclient.NodeTestUdpClient('nodetest.iot.oh.wsh.no',
                                                                          bind_port=random.randrange(1024, 9000))
        self.register(prefix='nc', nodeclient=self.nodeclient)


if __name__ == '__main__':
    proxytest = ProxyTest()
    proxytest.nodeclient.blue_led.on()
    udpserver = prometheus.server.socketserver.udp.UdpSocketServer(proxytest)
