CC=tools/micropython/mpy-cross/mpy-cross

all: 
	$(CC) src/core/python/prometheus.py
	$(CC) src/core/python/prometheus_servers.py
	$(CC) src/core/python/prometheus_esp8266.py
	mv src/core/python/*.mpy build/core/python/
	cd tools && ./micropython-make.sh
