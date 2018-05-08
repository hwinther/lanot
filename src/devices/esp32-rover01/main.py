import rover01
import prometheus.server
import prometheus.server.multiserver
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.tcp
import prometheus.server.socketserver.jsonrest
import prometheus.tftpd
import prometheus.logging as logging
import prometheus.pgc as gc
import time

gc.collect()

ST_STOPPED = 0
ST_DRIVING = 1


class LocalEvents(prometheus.server.Server):
    def __init__(self, instance):
        """

        :type instance: rover01.Rover01
        """
        prometheus.server.Server.__init__(self, instance)
        self.timer = 0
        self.state = ST_STOPPED

    def pre_loop(self, **kwargs):
        self.timer = time.time()
        self.instance.ssd.fill(False)
        self.instance.ssd.text('v: %s' % self.version(), 0, 0)
        self.instance.ssd.show()

    def loop_tick(self, **kwargs):
        if self.state is ST_STOPPED and self.instance.driving is not 0:
                self.state = ST_DRIVING
                # print('now driving: %s' + self.instance.driving)

        diff = time.time() - self.instance.driving
        # print(diff)
        if self.state is ST_DRIVING and self.instance.driving != 0 and diff >= 2:
            # print('over 2 sec since driving')
            # if self.state is ST_DRIVING and self.instance.driving:
            self.state = ST_STOPPED
            print('full stop')
            self.instance.full_stop()

        if time.time() - self.timer >= 1:
            self.timer = time.time()
            # print('1 sec event, diff=%d' % diff)
            assert isinstance(self.instance, rover01.Rover01)

            if self.state == ST_STOPPED:
                st = 'stopped'
            else:
                st = 'driving'

            # ssd_timer = time.time()
            self.instance.ssd.fill(False)
            self.instance.ssd.text('v: %s' % self.version(), 0, 0)
            self.instance.ssd.text('st: %s' % st, 0, 10)
            self.instance.ssd.text('s: %s' % self.timer, 0, 20)
            self.instance.ssd.show()
            # print(time.time() - ssd_timer)


def td():
    prometheus.tftpd.tftpd()


node = rover01.Rover01()
multiserver = prometheus.server.multiserver.MultiServer()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())

udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()
#
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
