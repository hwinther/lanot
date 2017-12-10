import greenhouse02
import prometheus_servers
import prometheus_tftpd
import prometheus_servers_ssl
import prometheus_logging as logging
import gc


gc.collect()


def td():
    prometheus_tftpd.tftpd()


node = greenhouse02.Greenhouse02()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())
multiserver = prometheus_servers.MultiServer()

udpserver = prometheus_servers.UdpSocketServer(node)
multiserver.add(udpserver, bind_host='', bind_port=9190)
gc.collect()

# tcpserver = prometheus_servers.TcpSocketServer(node)
# multiserver.add(tcpserver, bind_host='', bind_port=9191)
# gc.collect()

jsonrestserver = prometheus_servers.JsonRestServer(node,
                                                   loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_host='', bind_port=8080)
gc.collect()

# jsonrestsslserver = prometheus_servers.JsonRestServer(node,
#                                                       loop_tick_delay=0.1,  # for cpython, limits cpu cycles
#                                                       socketwrapper=prometheus_servers_ssl.SslSocket)
# multiserver.add(jsonrestsslserver, bind_host='', bind_port=4443)
# gc.collect()

logging.boot(udpserver)
multiserver.start()
