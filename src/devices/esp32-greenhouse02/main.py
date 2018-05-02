import greenhouse02
import servers.multiserver
import servers.socketserver.udp
import servers.socketserver.jsonrest
import prometheus_tftpd
import prometheus_logging as logging
import prometheus_gc as gc

gc.collect()


def td():
    prometheus_tftpd.tftpd()


node = greenhouse02.Greenhouse02()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())
multiserver = servers.multiserver.MultiServer()

udpserver = servers.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()

# tcpserver = prometheus_servers.TcpSocketServer(node)
# multiserver.add(tcpserver, bind_host='', bind_port=9195)
# gc.collect()

jsonrestserver = servers.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_port=8080)
gc.collect()

# jsonrestsslserver = prometheus_servers.JsonRestServer(node,
#                                                       loop_tick_delay=0.1,  # for cpython, limits cpu cycles
#                                                       socketwrapper=prometheus_servers_ssl.SslSocket)
# multiserver.add(jsonrestsslserver, bind_host='', bind_port=4443)
# gc.collect()

logging.boot(udpserver)
multiserver.start()
