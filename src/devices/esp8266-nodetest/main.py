import nodetest
import prometheus_servers
import prometheus_logging as logging
import gc


gc.collect()

node = nodetest.NodeTest()

gc.collect()
logging.debug(gc.mem_free())
multiserver = prometheus_servers.MultiServer()

udpserver = prometheus_servers.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()

tcpserver = prometheus_servers.TcpSocketServer(node)
multiserver.add(tcpserver)
gc.collect()

jsonrestserver = prometheus_servers.JsonRestServer(node, loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_port=8080)
gc.collect()

logging.boot(udpserver)
multiserver.start()
# udpserver.start()
