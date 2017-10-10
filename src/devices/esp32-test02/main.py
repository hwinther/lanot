import test02
import prometheus_servers
import prometheus_tftpd
import gc


gc.collect()


def td():
    prometheus_tftpd.tftpd()


node = test02.Test02()
ns = prometheus_servers.JsonRestServer(nt)
gc.collect()
gc.mem_free()
print(ns.uname())
ns.start()
