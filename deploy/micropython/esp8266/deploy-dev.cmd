@echo off
rem c:\python27\python -m esptool --port %1 erase_flash
c:\python27\python -m esptool --chip esp8266 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash --verify --flash_size=detect --flash_mode=qio 0 NODEMCUESP12E-v1.20.0-p0.2.4-1-g132cca417-dirty-2023-06-28.bin
