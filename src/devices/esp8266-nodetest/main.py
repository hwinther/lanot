import nodetest
import prometheus_servers
import gc


gc.collect()

nt = nodetest.NodeTest()
ns = prometheus_servers.JsonRestServer(nt)
gc.collect()
ns.start()
