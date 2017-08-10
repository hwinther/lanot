import sensor01
import prometheus_servers
import gc


gc.collect()

nt = sensor01.Sensor01()
# ns = prometheus_servers.JsonRestServer(nt)
gc.collect()
# ns.start()

multiserver = prometheus_servers.MultiServer()

udpserver = prometheus_servers.UdpSocketServer(nt)
multiserver.add(udpserver, bind_host='', bind_port=9195)

gc.collect()

jsonrestserver = prometheus_servers.JsonRestServer(nt)
multiserver.add(jsonrestserver, bind_host='', bind_port=8080)

gc.collect()
print(gc.mem_free())

multiserver.start()
