export PATH=/home/crono/esp-open-sdk/xtensa-lx106-elf/bin:/home/crono/xtensa-esp32-elf/bin:$PATH
export IDF_PATH=/home/crono/esp-idf
export ESPIDF=/home/crono/esp-idf
# export MICROPY_PY_FUNCTION_ATTRS=1

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
# export MICROPY_HW_BOARD_NAME="LoLin-ESP-12E"
# export MICROPY_HW_MCU_NAME="xtensa-lx106-32"
# make axtls &&
make -e MICROPY_PY_FUNCTION_ATTRS=1 && cp build/firmware-combined.bin ../../../../deploy/micropython/esp8266/$mpyversion-$mpybuilddate.bin

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making cc3200-WIPY $mpyversion-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
cd ../cc3200
# unset MICROPY_HW_BOARD_NAME
# unset MICROPY_HW_MCU_NAME
make -e BTARGET=bootloader BTYPE=release BOARD=WIPY && cp bootmgr/build/WIPY/release/bootloader.bin ../../../../deploy/micropython/wipy/custom/bootloader-$mpyversion-$mpybuilddate.bin
make -e BTARGET=application BTYPE=release BOARD=WIPY && cp build/WIPY/release/mcuimg.bin ../../../../deploy/micropython/wipy/custom/mcuimg-$mpyversion-$mpybuilddate.bin && unlink ../../../../deploy/micropython/wipy/custom/mcuimg.bin && ln -s ../../../../deploy/micropython/wipy/custom/mcuimg-$mpyversion-$mpybuilddate.bin ../../../../deploy/micropython/wipy/custom/mcuimg.bin

cd ../esp32
printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp32 $mpyversion-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
# export MICROPY_HW_BOARD_NAME="NodeMCU-ESP-32S"
# export MICROPY_HW_MCU_NAME="xtensa-lx6-32"
make -e && cp build/firmware.bin ../../../../deploy/micropython/esp32/$mpyversion-$mpybuilddate.bin
