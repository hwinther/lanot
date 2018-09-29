import greenhouse02
import prometheus.server.multiserver
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.tcp
import prometheus.server.socketserver.jsonrest
import prometheus.tftpd
import prometheus.logging as logging
import prometheus.pgc as gc
import time

gc.collect()


def td():
    prometheus.tftpd.tftpd()


class LocalEvents(prometheus.server.Server):
    def __init__(self, instance):
        """

        :type instance: rover01.Rover01
        """
        prometheus.server.Server.__init__(self, instance)
        self.timer = 0

    def pre_loop(self, **kwargs):
        self.timer = time.time()
        self.instance.ssd.ssd.fill(False)
        self.instance.ssd.ssd.text('v: %s' % self.version(), 0, 0)
        self.instance.ssd.ssd.show()

    def loop_tick(self, **kwargs):
        diff = time.time() - self.timer
        if diff >= 1:
            self.timer = time.time()
            # print('1 sec event, diff=%d' % diff)
            assert isinstance(self.instance, greenhouse02.Greenhouse02)
            """
            # update the screen with current values
            h1 = self.instance.hygrometer01.read()
            h2 = self.instance.hygrometer02.read()
            h3 = self.instance.hygrometer03.read()
            h4 = self.instance.hygrometer04.read()

            # self.instance.ssd.fill(False)
            self.instance.ssd.ssd.text('v: %s' % self.version(), 0, 0)
            self.instance.ssd.ssd.text('t: %d o: %s' % (time.time(), wlan.isconnected()), 0, 10)
            if wlan.isconnected():
                self.instance.ssd.ssd.text('i:%s' % wlan.ifconfig()[0], 0, 20)
            self.instance.ssd.ssd.text('h1:%d h2:%d' % (h1, h2), 0, 30)
            self.instance.ssd.ssd.text('h3:%d h4:%d' % (h3, h4), 0, 40)
            self.instance.ssd.ssd.show()
            """


node = greenhouse02.Greenhouse02()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())
multiserver = prometheus.server.multiserver.MultiServer()

udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()

tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
multiserver.add(tcpserver)
gc.collect()

jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_port=8080)
gc.collect()

# jsonrestsslserver = prometheus_servers.JsonRestServer(node,
#                                                       loop_tick_delay=0.1,  # for cpython, limits cpu cycles
#                                                       socketwrapper=prometheus_servers_ssl.SslSocket)
# multiserver.add(jsonrestsslserver, bind_host='', bind_port=4443)
# gc.collect()

localevents = LocalEvents(node)
multiserver.add(localevents)

logging.boot(udpserver)
multiserver.start()
