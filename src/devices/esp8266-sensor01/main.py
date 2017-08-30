import sensor01
import prometheus_servers
import gc


gc.collect()

node = sensor01.Sensor01()
udpserver = prometheus_servers.UdpSocketServer(node)
gc.collect()
print(udpserver.uname())
gc.collect()
print(gc.mem_free())

udpserver.start()
