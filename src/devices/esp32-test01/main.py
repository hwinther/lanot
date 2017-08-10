import test01
import prometheus_servers
import gc


gc.collect()

nt = test01.Test01()
ns = prometheus_servers.JsonRestServer(nt)
gc.collect()
gc.mem_free()
ns.start()
