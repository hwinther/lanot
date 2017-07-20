import sensor01
import prometheus_servers
import gc


gc.collect()

nt = sensor01.Sensor01()
ns = prometheus_servers.JsonRestServer(nt)
gc.collect()
ns.start()
