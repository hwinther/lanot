@echo off
rem python -m esptool --port %1 erase_flash
python -m esptool --chip esp8266 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash --verify --flash_size=detect --flash_mode=qio 0 v1.9.4-199-g6fc84a74-dirty-2018-06-24.bin
