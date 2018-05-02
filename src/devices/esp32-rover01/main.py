import rover01
import servers
import servers.multiserver
import servers.socketserver.udp
import servers.socketserver.tcp
import servers.socketserver.jsonrest
import prometheus_tftpd
import prometheus_logging as logging
import prometheus_gc as gc
import time


gc.collect()


ST_STOPPED = 0
ST_DRIVING = 1


class LocalEvents(servers.Server):
    def __init__(self, instance):
        """

        :type instance: rover01.Rover01
        """
        servers.Server.__init__(self, instance)
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
    prometheus_tftpd.tftpd()


node = rover01.Rover01()
multiserver = servers.multiserver.MultiServer()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())

udpserver = servers.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()
#
tcpserver = servers.socketserver.tcp.TcpSocketServer(node)
multiserver.add(tcpserver)
gc.collect()

jsonrestserver = servers.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
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
