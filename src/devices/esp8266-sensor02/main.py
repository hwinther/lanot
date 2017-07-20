import sensor02
import prometheus_servers
import gc


gc.collect()

nt = sensor02.Sensor02()
ns = prometheus_servers.JsonRestServer(nt)
gc.collect()
ns.start()
