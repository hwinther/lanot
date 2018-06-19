import prometheus
import prometheus.dht11
import prometheus.server.multiserver
import prometheus.server.socketserver.tcp
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.jsonrest
from prometheus.server.socketserver.sslsocket import SslSocket
import prometheus.logging as logging
import machine
# import pickle
# from guppy import hpy


class LocalTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.blue_led = prometheus.Led(machine.Pin(14, machine.Pin.OUT))
        self.register(prefix='b', blue_led=self.blue_led)

        self.red_led = prometheus.Led(machine.Pin(15, machine.Pin.OUT))
        self.register(prefix='r', red_led=self.red_led)

        self.dht11 = prometheus.dht11.Dht11(machine.Pin(13, machine.Pin.OUT))
        self.register(prefix='d', dht11=self.dht11)

        self.hygrometer = prometheus.Adc(0)
        self.register(prefix='h', hygrometer=self.hygrometer)


if __name__ == '__main__':
    node = LocalTest()

    # multiserver = prometheus.server.multiserver.MultiServer()

    udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
    # multiserver.add(udpserver)
    #
    # tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
    # multiserver.add(tcpserver)
    #
    # jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
    # multiserver.add(jsonrestserver, bind_port=8080)

    # loop_tick_delay is for cpython, limits cpu cycles
    # jsonrestsslserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node,
    #                                                                            loop_tick_delay=0.1,
    #                                                                            socketwrapper=SslSocket)
    # multiserver.add(jsonrestsslserver, bind_port=4443)

    # s = pickle.dumps(node)
    # print('len(s)=%d' % len(s))

    logging.boot(udpserver)
    # multiserver.start()
    udpserver.start()

    # rsaserver = prometheus_crypto.RsaUdpSocketServer(localtest, clientencrypt=False)
    # rsaserver.start()
    # hp = hpy()  # this is to trace memory usage
    # before = hp.heap()

    # critical section here
    # try:
    # udpserver.start()
    # except:
    #     pass

    # after = hp.heap()
    # leftover = after - before
    # import pdb

    # pdb.set_trace()
