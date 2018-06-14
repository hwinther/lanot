python -m esptool --chip esp32 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash -z 0x1000 x
