#!/bin/bash
/home/crono/micropython/mpy-cross/mpy-cross -mno-unicode src/core/python/prometheus.py
/home/crono/micropython/mpy-cross/mpy-cross -mno-unicode src/core/python/prometheus_esp8266.py
mv src/core/python/*.mpy build/core/python/
