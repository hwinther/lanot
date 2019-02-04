import gc
import prometheus.device

gc.collect()


class NodeTest(prometheus.device.Esp8266Pcb):
    def __init__(self):
        prometheus.device.Esp8266Pcb.__init__(self, enable_i2c=True)  # , neopixel_amount=256, neopixel_pin=12)
