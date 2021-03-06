import prometheus
import prometheus.dht11
import prometheus.server.multiserver
import prometheus.server.socketserver.tcp
import prometheus.server.socketserver.udp
# import prometheus.server.socketserver.udp2
import prometheus.server.socketserver.jsonrest
# from prometheus.server.socketserver.sslsocket import SslSocket
import prometheus.server.console
import prometheus.logging as logging
import prometheus.pssd1306
import machine
import sys
# import pickle
# from guppy import hpy


class LocalTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.digital0 = prometheus.Digital(machine.Pin(0, machine.Pin.OUT))
        self.register(prefix='t', digital0=self.digital0)

        self.blue_led = prometheus.Led(machine.Pin(14, machine.Pin.OUT))
        self.register(prefix='b', blue_led=self.blue_led)

        self.red_led = prometheus.Led(machine.Pin(15, machine.Pin.OUT))
        self.register(prefix='r', red_led=self.red_led)

        self.dht11 = prometheus.dht11.Dht11(machine.Pin(13, machine.Pin.OUT))
        self.register(prefix='d', dht11=self.dht11)

        self.hygrometer = prometheus.Adc(0)
        self.register(prefix='h', hygrometer=self.hygrometer)

        # self.i2c = machine.I2C(scl=machine.Pin(0), sda=machine.Pin(4), freq=400000)
        # logging.info('i2c: %s' % self.i2c.scan())

        # self.ssd = prometheus.pssd1306.SSD1306(self.i2c)
        # self.register(prefix='ss', ssd=self.ssd)

        # self.ssd.text('init', 0, 0)

    @prometheus.Registry.register('LocalTest', '1', 'OUT')
    def test1(self, **kwargs):
        """
        Returns True as bool
        :param kwargs:
        :return: bool
        """
        return True

    @prometheus.Registry.register('LocalTest', '2', 'OUT')
    def test2(self, **kwargs):
        """
        Returns False as bool
        :param kwargs:
        :return: bool
        """
        return False

    @prometheus.Registry.register('LocalTest', '3', 'OUT')
    def test3(self, **kwargs):
        """
        Returns None explicitly
        :param kwargs:
        :return: bool
        """
        return None

    @prometheus.Registry.register('LocalTest', '4')
    def test4(self, **kwargs):
        """
        Returns None implicitly
        :param kwargs:
        :return: bool
        """

    @prometheus.Registry.register('LocalTest', '5', 'OUT')
    def test5(self, **kwargs):
        """
        Returns 0 as int
        :param kwargs:
        :return: int
        """
        return 0

    @prometheus.Registry.register('LocalTest', '6', 'OUT')
    def test6(self, **kwargs):
        """
        Returns 'test'
        :param kwargs:
        :return: str
        """
        return 'test'

    @prometheus.Registry.register('LocalTest', '7', 'OUT')
    def test7(self, **kwargs):
        """
        Returns b'test'
        :param kwargs:
        :return: bytes
        """
        return b'test'

    @prometheus.Registry.register('LocalTest', '8', 'OUT')
    def test8(self, input=None, **kwargs):
        """
        Returns echo of input
        :param input: Any
        :param kwargs:
        :return: Any
        """
        return input


if __name__ == '__main__':
    node = LocalTest()

    multiserver = prometheus.server.multiserver.MultiServer()

    udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
    multiserver.add(udpserver)

    tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
    multiserver.add(tcpserver)

    jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
    multiserver.add(jsonrestserver, bind_port=8080)

    # console = prometheus.server.console.Console(node)
    # multiserver.add(console)

    # loop_tick_delay is for cpython, limits cpu cycles
    # jsonrestsslserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node,
    #                                                                            loop_tick_delay=0.1,
    #                                                                            socketwrapper=SslSocket)
    # multiserver.add(jsonrestsslserver, bind_port=4443)

    # s = pickle.dumps(node)
    # print('len(s)=%d' % len(s))

    logging.boot(udpserver)
    multiserver.start()
    # udpserver.start()

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
