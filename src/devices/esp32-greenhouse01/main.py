import greenhouse01
import prometheus.server.multiserver
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.jsonrest
import prometheus.tftpd
import prometheus.logging as logging
import prometheus.pgc as gc

gc.collect()


def td():
    prometheus.tftpd.tftpd()


node = greenhouse01.Greenhouse01()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())
multiserver = prometheus.server.multiserver.MultiServer()

udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()

# tcpserver = prometheus_servers.TcpSocketServer(node)
# multiserver.add(tcpserver, bind_host='', bind_port=9195)
# gc.collect()

jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_port=8080)
gc.collect()

# jsonrestsslserver = prometheus_servers.JsonRestServer(node,
#                                                       loop_tick_delay=0.1,  # for cpython, limits cpu cycles
#                                                       socketwrapper=prometheus_servers_ssl.SslSocket)
# multiserver.add(jsonrestsslserver, bind_host='', bind_port=4443)
# gc.collect()

logging.boot(udpserver)
multiserver.start()
