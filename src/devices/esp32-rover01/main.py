import rover01
import prometheus_servers
import prometheus_tftpd
import prometheus_logging as logging
import gc
import machine
import time


gc.collect()


ST_STOPPED = 0
ST_DRIVING = 1


class LocalEvents(prometheus_servers.Server):
    def __init__(self, instance):
        """

        :type instance: rover01.Rover01
        """
        prometheus_servers.Server.__init__(self, instance)
        self.timer = 0
        self.state = ST_STOPPED

    def pre_loop(self, **kwargs):
        self.timer = time.time()
        self.instance.ssd.fill(False)
        self.instance.ssd.text('v: %s' % self.version(), 0, 0)
        self.instance.ssd.show()

    def loop_tick(self, **kwargs):
        if self.state is ST_STOPPED and self.instance.driving:
                self.state = ST_DRIVING
                print('now driving')

        if time.time() - self.timer >= 2:
            self.timer = time.time()
            print('1s')
            assert isinstance(self.instance, rover01.Rover01)

            if self.state is ST_DRIVING and self.instance.driving:
                self.state = ST_STOPPED
                print('full stop')
                self.instance.full_stop()

            if self.state == ST_STOPPED:
                st = 'stopped'
            else:
                st = 'driving'

            self.instance.ssd.fill(False)
            self.instance.ssd.text('st: %s' % st, 0, 0)
            self.instance.ssd.text('s: %s' % self.timer, 0, 10)
            self.instance.ssd.show()


def td():
    prometheus_tftpd.tftpd()


node = rover01.Rover01()
multiserver = prometheus_servers.MultiServer()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())

udpserver = prometheus_servers.UdpSocketServer(node)
multiserver.add(udpserver, bind_host='', bind_port=9190)
gc.collect()
#
tcpserver = prometheus_servers.TcpSocketServer(node)
multiserver.add(tcpserver, bind_host='', bind_port=9191)
gc.collect()

jsonrestserver = prometheus_servers.JsonRestServer(node,
                                                   loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_host='', bind_port=8080)
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
