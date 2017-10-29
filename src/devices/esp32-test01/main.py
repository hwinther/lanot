import test01
import prometheus_servers
import prometheus_tftpd
import gc


gc.collect()


def td():
    prometheus_tftpd.tftpd()


node = test01.Test01()
ns = prometheus_servers.JsonRestServer(node)
gc.collect()
gc.mem_free()
print(ns.uname())
ns.start()
