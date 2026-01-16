python -m esptool --chip esp32 --port %1 --baud 921600 --before default-reset --after hard-reset write-flash -z 0x1000 v1.9.4-140-g8fb95d65-dirty-2018-06-14-prometheus-0.1.8a.bin
