@echo off
python -m esptool --chip esp32 --port %1 --baud 921600 --before default-reset --after hard-reset write-flash -z 0x1000 NODEMCU32S-v1.20.0-2026-01-11.bin
