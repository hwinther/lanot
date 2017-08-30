import test01
import prometheus_servers
import prometheus_tftpd
import gc


gc.collect()


def td():
    prometheus_tftpd.tftpd()

nt = test01.Test01()
ns = prometheus_servers.JsonRestServer(nt)
gc.collect()
gc.mem_free()
print(ns.uname())
ns.start()
