@echo off
python -m esptool --chip esp8266 --port %1 --baud 921600 --before default-reset --after hard-reset write-flash --verify --flash-size=detect --flash-mode=qio 0 v1.9.4-568-g4df194394-dirty-2018-09-24-prometheus-0.1.9.bin
