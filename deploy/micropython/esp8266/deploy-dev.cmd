@echo off
python -m esptool --chip esp8266 --port %1 --baud 921600 --before default-reset --after hard-reset write-flash --flash-size=detect --flash-mode=qio 0 NODEMCUESP12E-v1.20.0-p0.2.4-1-g132cca417-dirty-2023-06-28.bin
