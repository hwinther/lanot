import nodetest
import prometheus_servers
import prometheus_crypto
import gc


gc.collect()

node = nodetest.NodeTest()
udpserver = prometheus_crypto.RsaUdpSocketServer(node)
gc.collect()
print(udpserver.uname())
gc.collect()
print(gc.mem_free())

udpserver.start()

# ns.start()
# multiserver = prometheus_servers.MultiServer()
# multiserver.add(udpserver, bind_host='', bind_port=9195)
# jsonrestserver = prometheus_servers.JsonRestServer(nt)
# multiserver.add(jsonrestserver, bind_host='', bind_port=8080)
