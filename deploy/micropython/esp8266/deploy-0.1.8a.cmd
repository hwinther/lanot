@echo off
python -m esptool --port %1 erase_flash
python -m esptool --chip esp8266 --port %1 --baud 512000 --before default_reset --after hard_reset write_flash --verify --flash_size=detect --flash_mode=qio 0 v1.9.4-140-g8fb95d65-dirty-2018-06-14-prometheus-0.1.8a.bin
