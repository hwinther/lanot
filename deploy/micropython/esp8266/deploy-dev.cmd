@echo off
python -m esptool --port %1 erase_flash
python -m esptool --chip esp8266 --port %1 --baud 512000 --before default_reset --after hard_reset write_flash --verify --flash_size=detect --flash_mode=qio 0 x
