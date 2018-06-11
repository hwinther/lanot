# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import gc
import os
import prometheus.pnetwork

gc.collect()

prometheus.pnetwork.init_network()
print(os.uname())
gc.collect()
