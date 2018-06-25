@echo off
python -m esptool --chip esp32 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash -z 0x1000 v1.9.4-199-g6fc84a74-dirty-2018-06-25.bin
