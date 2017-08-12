import prometheus
import prometheus_esp8266
import machine
import gc


gc.collect()


class Test01(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
