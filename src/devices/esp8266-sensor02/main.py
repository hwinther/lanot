import sensor02
import prometheus.server.socketserver.udp
import prometheus.pgc as gc

gc.collect()

node = sensor02.Sensor02()
udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
gc.collect()
print(udpserver.uname())
gc.collect()
print(gc.mem_free())

udpserver.start()
