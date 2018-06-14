python -m esptool --chip esp32 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash -z 0x1000 v1.9.3-607-g12a3fccc-dirty-2018-05-08-prometheus-0.1.6.bin
