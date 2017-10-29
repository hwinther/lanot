export PATH=/home/crono/esp-open-sdk/xtensa-lx106-elf/bin:/home/crono/xtensa-esp32-elf/bin:$PATH
export IDF_PATH=/home/crono/esp-idf
export ESPIDF=/home/crono/esp-idf

cd micropython
printf "${BLUE}*****************************${NC}\n"
printf "${BLUE}* Making mpy cross compiler *${NC}\n"
printf "${BLUE}*****************************${NC}\n"
make -C mpy-cross MICROPY_PY_FUNCTION_ATTRS=1
export mpyversion=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_GIT_TAG | cut -d' ' -f3 | cut -d'"' -f2`
export mpybuilddate=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_BUILD_DATE | cut -d' ' -f3 | cut -d'"' -f2`

cd esp8266
printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp8266 $mpyversion-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
make axtls MICROPY_PY_FUNCTION_ATTRS=1 && make MICROPY_PY_FUNCTION_ATTRS=1 && cp build/firmware-combined.bin ../../../deploy/micropython/esp8266/$mpyversion-$mpybuilddate.bin

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making cc3200-WIPY $mpyversion-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
cd ../cc3200
make BTARGET=bootloader BTYPE=release BOARD=WIPY MICROPY_PY_FUNCTION_ATTRS=1 && cp bootmgr/build/WIPY/release/bootloader.bin ../../../deploy/micropython/wipy/custom/bootloader-$mpyversion-$mpybuilddate.bin
make BTARGET=application BTYPE=release BOARD=WIPY MICROPY_PY_FUNCTION_ATTRS=1 && cp build/WIPY/release/mcuimg.bin ../../../deploy/micropython/wipy/custom/mcuimg-$mpyversion-$mpybuilddate.bin && unlink ../../../deploy/micropython/wipy/custom/mcuimg.bin && ln -s ../../../deploy/micropython/wipy/custom/mcuimg-$mpyversion-$mpybuilddate.bin ../../../deploy/micropython/wipy/custom/mcuimg.bin

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making (esp32) mpy cross compiler *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
cd ../../micropython-esp32
make -C mpy-cross MICROPY_PY_FUNCTION_ATTRS=1
export mpyversion=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_GIT_TAG | cut -d' ' -f3 | cut -d'"' -f2`
export mpybuilddate=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_BUILD_DATE | cut -d' ' -f3 | cut -d'"' -f2`
cd esp32
printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp32 $mpyversion-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
make MICROPY_PY_FUNCTION_ATTRS=1 && cp build/firmware.bin ../../../deploy/micropython/esp32/$mpyversion-$mpybuilddate.bin
