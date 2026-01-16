@echo off
python -m esptool --chip esp8266 --port %1 --baud 512000 --before default-reset --after hard-reset write-flash --verify --flash-size=detect --flash-mode=qio 0 v1.9.4-140-g8fb95d65-dirty-2018-06-14-prometheus-0.1.8a.bin
