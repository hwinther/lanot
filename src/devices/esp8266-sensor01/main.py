import sensor01
import servers.socketserver.udp
import prometheus_gc as gc

gc.collect()

node = sensor01.Sensor01()
udpserver = servers.socketserver.udp.UdpSocketServer(node)
gc.collect()
print(udpserver.uname())
gc.collect()
print(gc.mem_free())

udpserver.start()
