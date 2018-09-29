import nodetest
import machine
# import prometheus.server.multiserver
# import prometheus.server.socketserver.udp
import prometheus.server.socketserver.tcp
# import prometheus.server.socketserver.jsonrest
import prometheus.logging as logging
import prometheus.pgc as gc

gc.collect()

node = nodetest.NodeTest()
gc.collect()
# logging.debug('mem_free after adding node: %d' % gc.mem_free())

# multiserver = prometheus.server.multiserver.MultiServer()
# gc.collect()
# logging.debug('mem_free after adding multi: %d' % gc.mem_free())

# udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
# multiserver.add(udpserver)
# gc.collect()
# logging.debug('mem_free after adding udp: %d' % gc.mem_free())

tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
# multiserver.add(tcpserver)
gc.collect()
# logging.debug('mem_free after adding tcp: %d' % gc.mem_free())

# jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
# multiserver.add(jsonrestserver)
# gc.collect()
# logging.debug('mem_free after adding json: %d' % gc.mem_free())

logging.boot(tcpserver)
gc.collect()
logging.debug('mem_free before start: %d' % gc.mem_free())
# try:
tcpserver.start()
# except Exception as exception:
#     print(exception)
#     gc.collect()

try:
    logging.error('crashed? rst')
except Exception:
    gc.collect()

machine.reset()
