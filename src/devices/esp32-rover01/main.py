import rover01
import prometheus.server
import prometheus.server.multiserver
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.tcp
import prometheus.server.socketserver.jsonrest
import prometheus.server.console
import prometheus.tftpd
import prometheus.logging as logging
import prometheus.pgc as gc
import utime

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
        self.mse = 0

    def pre_loop(self, **kwargs):
        self.timer = utime.ticks_ms()
        self.instance.ssd.fill(False)
        self.instance.ssd.text('v: %s' % self.version(), 0, 0)
        self.instance.ssd.show()
        self.instance.full_stop()

    def loop_tick(self, **kwargs):
        if self.state is ST_STOPPED and self.instance.driving is not 0:
                self.state = ST_DRIVING
                # print('now driving: %s' + self.instance.driving)

        if self.instance.driving != 0:
            ms = utime.ticks_ms()
            # if ms > self.instance.driving:

            diff = abs(utime.ticks_diff(self.instance.driving, ms))
            # print(diff)
            if self.state is ST_DRIVING and diff >= 200:
                # print('over 2 sec since driving')
                self.state = ST_STOPPED
                logging.notice('full stop at diff %d, driving %d and ms %d' % (diff,
                                                                               self.instance.driving,
                                                                               ms))
                self.instance.full_stop()
                self.instance.driving = 0

        delta = abs(utime.ticks_diff(self.timer, utime.ticks_ms()))
        if delta >= 200:
            self.timer = utime.ticks_ms()
            # print('200ms event, delta %d' % delta)
            assert isinstance(self.instance, rover01.Rover01)

            self.mse += 1
            if self.mse >= 2:
                # print('400 ms?')
                self.mse = 0

            return
            if self.state == ST_STOPPED:
                st = 'stopped'
            else:
                st = 'driving'

            # logging.notice('updating ssd')
            self.instance.ssd.fill(False)
            self.instance.ssd.text('v: %s' % self.version(), 0, 0)
            self.instance.ssd.text('st: %s' % st, 0, 10)
            self.instance.ssd.text('s: %s' % self.timer, 0, 20)
            self.instance.ssd.show()


node = rover01.Rover01()
multiserver = prometheus.server.multiserver.MultiServer()
gc.collect()

udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()

tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
multiserver.add(tcpserver)
gc.collect()

localevents = LocalEvents(node)
multiserver.add(localevents)

logging.boot(udpserver)
multiserver.start()
