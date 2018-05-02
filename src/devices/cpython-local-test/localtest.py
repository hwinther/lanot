import prometheus
import prometheus_esp8266
import prometheus_servers
import prometheus_servers_ssl
import prometheus_logging as logging
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

        self.dht11 = prometheus_esp8266.Dht11(machine.Pin(13, machine.Pin.OUT))
        self.register(prefix='d', dht11=self.dht11)

        self.hygrometer = prometheus.Adc(0)
        self.register(prefix='h', hygrometer=self.hygrometer)


if __name__ == '__main__':
    node = LocalTest()

    multiserver = prometheus_servers.MultiServer()

    udpserver = prometheus_servers.UdpSocketServer(node)
    multiserver.add(udpserver)

    tcpserver = prometheus_servers.TcpSocketServer(node)
    multiserver.add(tcpserver)

    jsonrestserver = prometheus_servers.JsonRestServer(node, loop_tick_delay=0.1)
    multiserver.add(jsonrestserver, bind_port=8080)

    jsonrestsslserver = prometheus_servers.JsonRestServer(node, loop_tick_delay=0.1,  # for cpython, limits cpu cycles
                                                          socketwrapper=prometheus_servers_ssl.SslSocket)
    multiserver.add(jsonrestsslserver, bind_port=4443)

    # s = pickle.dumps(node)
    # print('len(s)=%d' % len(s))

    logging.boot(udpserver)
    multiserver.start()

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
