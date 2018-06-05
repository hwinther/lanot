import test03
import prometheus.pgc as gc
import prometheus.server.multiserver
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.tcp
import prometheus.server.socketserver.jsonrest
import prometheus.tftpd
import prometheus.logging as logging
import time

gc.collect()


def td():
    prometheus.tftpd.tftpd()


node = test03.Test03()
gc.collect()
logging.debug(gc.mem_free())
multiserver = prometheus.server.multiserver.MultiServer()


def scan(name=u'dgn'):
    line_height = 0
    node.ssd.fill(False)
    for s in wlan.scan():
        # (b'dgn.iot', b'\x00\x19\x07\x07Ua', 8, -62, 3, False)
        print(s)
        if s[0].startswith(name):
            print('showing on screen: %s' % s[0])
            id = list()
            _sum = 0
            for x in s[1]:
                id.append(str(hex(x)))
                _sum ^= x
            node.ssd.text('%s%d %d%d' % (s[0].decode('ansi'), _sum, s[2], s[3]), 0, line_height)
            line_height += 10
    node.ssd.show()


def scanloop(name=u'dgn'):
    while True:
        scan(name)
        time.sleep(1)


udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()

tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
multiserver.add(tcpserver)
gc.collect()

jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_port=8080)
gc.collect()

logging.boot(udpserver)
# multiserver.start()
scanloop('dni')
