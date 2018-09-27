@echo off
python -m esptool --chip esp32 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash -z 0x1000 v1.9.4-568-g4df194394-dirty-2018-09-27.bin
