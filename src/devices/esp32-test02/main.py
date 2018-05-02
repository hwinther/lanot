import test02
import servers.multiserver
import servers.socketserver.udp
import servers.socketserver.tcp
import servers.socketserver.jsonrest
import prometheus_tftpd
import prometheus_logging as logging
import prometheus_gc as gc


gc.collect()


def td():
    prometheus_tftpd.tftpd()


node = test02.Test02()
gc.collect()
logging.debug(gc.mem_free())
multiserver = servers.multiserver.MultiServer()

udpserver = servers.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()

tcpserver = servers.socketserver.tcp.TcpSocketServer(node)
multiserver.add(tcpserver)
gc.collect()

jsonrestserver = servers.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_port=8080)
gc.collect()

logging.boot(udpserver)
multiserver.start()
