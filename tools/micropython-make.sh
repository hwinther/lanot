#!/bin/bash
# ESP8266
export PATH=/mnt/Projects/lanot/tools/esp-open-sdk/xtensa-lx106-elf/bin:$PATH
# esptool.py from debian package
export PATH=/usr/share/esptool:$PATH
# WIPY/CC3200
export PATH=/mnt/Projects/lanot/tools/gcc-arm-none-eabi-10.3-2021.10/bin:$PATH
# ESP32
source /mnt/Projects/lanot/tools/esp-idf-5/export.sh

cd micropython
printf "${BLUE}*****************************${NC}\n"
printf "${BLUE}* Making mpy cross compiler *${NC}\n"
printf "${BLUE}*****************************${NC}\n"
make -C mpy-cross MICROPY_PY_FUNCTION_ATTRS=1
export mpyversion=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_GIT_TAG | cut -d' ' -f3 | cut -d'"' -f2`
export mpybuilddate=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_BUILD_DATE | cut -d' ' -f3 | cut -d'"' -f2`

cd ports

cd esp8266
printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp8266 $mpyversion-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
make -j BOARD=NODEMCUESP12E && cp build-NODEMCUESP12E/firmware-combined.bin ../../../../deploy/micropython/esp8266/NODEMCUESP12E-$mpyversion-$mpybuilddate.bin
make -j BOARD=LOLINESP32E && cp build-LOLINESP32E/firmware-combined.bin ../../../../deploy/micropython/esp8266/LOLINESP32E-$mpyversion-$mpybuilddate.bin
exit 0
cd ../esp32
printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp32 $mpyversion-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
make -j BOARD=NODEMCU32S && cp build-NODEMCU32S/firmware.bin ../../../../deploy/micropython/esp32/NODEMCU32S-$mpyversion-$mpybuilddate.bin

cd ../cc3200
printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making cc3200-WIPY $mpyversion-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
make -e BTARGET=bootloader BTYPE=release BOARD=WIPY && cp bootmgr/build/WIPY/release/bootloader.bin ../../../../deploy/micropython/wipy/custom/bootloader-$mpyversion-$mpybuilddate.bin
make -e BTARGET=application BTYPE=release BOARD=WIPY && cp build/WIPY/release/mcuimg.bin ../../../../deploy/micropython/wipy/custom/mcuimg-$mpyversion-$mpybuilddate.bin && unlink ../../../../deploy/micropython/wipy/custom/mcuimg.bin && ln -s ../../../../deploy/micropython/wipy/custom/mcuimg-$mpyversion-$mpybuilddate.bin ../../../../deploy/micropython/wipy/custom/mcuimg.bin
