CC=tools/micropython/mpy-cross/mpy-cross

all: 
	$(CC) src/core/python/prometheus.py
	$(CC) src/core/python/prometheus_crypto.py
	$(CC) src/core/python/prometheus_esp8266.py
	$(CC) src/core/python/prometheus_servers.py
	$(CC) src/core/python/prometheus_tftpd.py
	mv src/core/python/*.mpy deploy/core/python/
	cd tools && ./micropython-make.sh
