python -m esptool --chip esp32 --port %1 --baud 921600 --before default_reset --after hard_reset write_flash -z --flash_freq 80m --flash_mode dio --flash_size 4MB 0x1000 v1.9.2-445-g84035f0f-dirty-2017-12-04.bin
