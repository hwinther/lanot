# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import gc
# import webrepl
import prometheus.pnetwork
import os

# webrepl.start()
gc.collect()

prometheus.pnetwork.init_network()
print(os.uname())
