@echo off
rem python -m esptool --port %1 erase_flash
python -m esptool --chip esp8266 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash --verify --flash_size=detect --flash_mode=qio 0 v1.9.4-568-g4df194394-dirty-2018-09-24-prometheus-0.1.9.bin
