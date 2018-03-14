python -m esptool --chip esp32 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash -z 0x1000 v1.9.3-397-g0acf868b-dirty-2018-03-05.bin
rem --flash_freq 80m --flash_mode dio --flash_size 4MB
