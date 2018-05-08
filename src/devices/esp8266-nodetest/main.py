import nodetest
import prometheus.server.socketserver.udp
import prometheus.logging as logging
import prometheus.pgc as gc

gc.collect()

node = nodetest.NodeTest()

gc.collect()
logging.debug(gc.mem_free())
# multiserver = server.multiserver.MultiServer()

udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
# multiserver.add(udpserver)
# gc.collect()

# tcpserver = server.socketserver.tcp.TcpSocketServer(node)
# multiserver.add(tcpserver)
# gc.collect()

# jsonrestserver = server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
# multiserver.add(jsonrestserver, bind_port=8080)
gc.collect()

logging.boot(udpserver)
gc.collect()
logging.debug('mem_free before start: %d' % gc.mem_free())
# multiserver.start()
udpserver.start()
