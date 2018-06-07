import test02
import prometheus.pgc as gc
import prometheus.server.multiserver
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.tcp
import prometheus.server.socketserver.jsonrest
import prometheus.tftpd
import prometheus.logging as logging

gc.collect()


def td():
    prometheus.tftpd.tftpd()


node = test02.Test02()
gc.collect()
logging.debug(gc.mem_free())
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

logging.boot(udpserver)
multiserver.start()
