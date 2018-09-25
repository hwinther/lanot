# coding=utf-8
import gc
import prometheus.pnetwork

gc.collect()

prometheus.pnetwork.init_network()

gc.collect()
