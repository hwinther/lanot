import test02
import prometheus_servers
import prometheus_tftpd
import prometheus_logging as logging
import gc


gc.collect()


def td():
    prometheus_tftpd.tftpd()


node = test02.Test02()
gc.collect()
logging.debug(gc.mem_free())
multiserver = prometheus_servers.MultiServer()

udpserver = prometheus_servers.UdpSocketServer(node)
multiserver.add(udpserver, bind_host='', bind_port=9190)
gc.collect()

tcpserver = prometheus_servers.TcpSocketServer(node)
multiserver.add(tcpserver, bind_host='', bind_port=9191)
gc.collect()

jsonrestserver = prometheus_servers.JsonRestServer(node,
                                                   loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_host='', bind_port=8080)
gc.collect()

logging.boot(udpserver)
multiserver.start()
