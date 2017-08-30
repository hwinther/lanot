import sensor02
import prometheus_servers
import gc


gc.collect()

node = sensor02.Sensor02()
udpserver = prometheus_servers.UdpSocketServer(node)
gc.collect()
print(udpserver.uname())
gc.collect()
print(gc.mem_free())

udpserver.start()
