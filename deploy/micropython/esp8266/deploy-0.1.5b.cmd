python -m esptool --chip esp8266 --port %1 erase_flash
python -m esptool --chip esp8266 --port %1 --baud 921600 write_flash 0x0 v1.9.3-397-g0acf868b-dirty-2018-05-02-prometheus-0.1.5b.bin
