#!/bin/bash
set -e

cd micropython
# For CI builds, ensure we have all tags in case we have a shallow clone
git fetch --tags -q
echo "Building $(git describe --tags --dirty --always)"

printf "${BLUE}*****************************${NC}\n"
printf "${BLUE}* Making mpy cross compiler *${NC}\n"
printf "${BLUE}*****************************${NC}\n"
mpy-make() {
    sudo docker run --rm -v $(pwd)/../../:/opt/lanot -w /opt/lanot/tools/micropython --entrypoint make ghcr.io/hwinther/lanot/mpy-cross:13 "$@"
}
# Temporary hack, later all SDKs should use the same debian version
mpy-bullseye-make() {
    sudo docker run --rm -v $(pwd)/../../:/opt/lanot -w /opt/lanot/tools/micropython --entrypoint make ghcr.io/hwinther/lanot/mpy-cross:bullseye "$@"
}
# mpy-bullseye-make -C mpy-cross clean
mpy-bullseye-make -C mpy-cross MICROPY_PY_FUNCTION_ATTRS=1
# mpy-make -C mpy-cross MICROPY_PY_FUNCTION_ATTRS=1
# /hack - after libc issues are restored, just use mpy-make
echo "mpy-cross version defines:"
cat mpy-cross/build/genhdr/mpversion.h
export mpyversion=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_GIT_TAG | cut -d' ' -f3 | cut -d'"' -f2`
export mpybuilddate=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_BUILD_DATE | cut -d' ' -f3 | cut -d'"' -f2`
export prometheus_version=`cat ../../src/core/prometheus/__init__.py | grep __version__ | cut -d"'" -f2`

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp8266 $mpyversion-p$prometheus_version-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
esp8266-make() {
    sudo docker run --rm -v $(pwd)/../../:/opt/lanot -w /opt/lanot/tools/micropython --entrypoint bash ghcr.io/hwinther/lanot/esp-open-sdk:2.1.0 -c "git config --global --add safe.directory '*' && git describe --tags --dirty --always && git status --porcelain && make $*"
}
esp8266-make -C ports/esp8266 submodules
esp8266-make -C ports/esp8266 -j BOARD=NODEMCUESP12E
echo "esp8266 NODEMCUESP12E version defines:"
cat ports/esp8266/build-NODEMCUESP12E/genhdr/mpversion.h
cp -v ports/esp8266/build-NODEMCUESP12E/firmware.bin ../../deploy/micropython/esp8266/NODEMCUESP12E-$mpyversion-p$prometheus_version-$mpybuilddate.bin
esp8266-make -C ports/esp8266 -j BOARD=LOLINESP32E
echo "esp8266 LOLINESP32E version defines:"
cat ports/esp8266/build-LOLINESP32E/genhdr/mpversion.h
cp -v ports/esp8266/build-LOLINESP32E/firmware.bin ../../deploy/micropython/esp8266/LOLINESP32E-$mpyversion-p$prometheus_version-$mpybuilddate.bin

# Temporary hack, later all SDKs should use the same debian version
# mpy-make -C mpy-cross clean
mpy-make -C mpy-cross MICROPY_PY_FUNCTION_ATTRS=1
# /hack

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp32 $mpyversion-p$prometheus_version-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
esp32-make() {
    sudo docker run --rm -v $(pwd)/../../:/opt/lanot -w /opt/lanot -e IDF_PATH=/opt/sdk/esp-idf --entrypoint bash --privileged -u 0 ghcr.io/hwinther/lanot/esp-idf-5:5.5.1 -c "set -x && source /opt/sdk/esp-idf/export.sh && git config --global --add safe.directory '*' && mkdir -p /opt/local && cp -rd /opt/lanot /opt/local/lanot && cd /opt/local/lanot/tools/micropython && git describe --tags --dirty --always && git status --porcelain && cd ports/esp32 && make BOARD=NODEMCU32S submodules && make BOARD=NODEMCU32S && echo \"esp32 NODEMCU32S version defines:\" && cat build-NODEMCU32S/genhdr/mpversion.h && make BOARD=NODEMCU32S BOARD_VARIANT=SPIRAM && find . -type f \( -name \*.bin -or -name \*.elf -or -name \*.map -or -name sdkconfig -or -name flash_args \) -path \*/build-\*/\* -not -path \*/CMakeFiles/\* -exec cp --parents {} /opt/lanot/tools/micropython/ports/esp32/ \;"
}
esp32-make
cp -v ports/esp32/build-NODEMCU32S/firmware.bin ../../deploy/micropython/esp32/NODEMCU32S-$mpyversion-p$prometheus_version-$mpybuilddate.bin
cp -v ports/esp32/build-NODEMCU32S-SPIRAM/firmware.bin ../../deploy/micropython/esp32/NODEMCU32S-SPIRAM-$mpyversion-p$prometheus_version-$mpybuilddate.bin

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making cc3200-WIPY $mpyversion-p$prometheus_version-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
cc3200-make() {
    sudo docker run --rm -v $(pwd)/../../:/opt/lanot -w /opt/lanot/tools/micropython --entrypoint make ghcr.io/hwinther/lanot/gcc-arm-none-eabi:10.3-2021.10 "$@"
}
cc3200-make -C ports/cc3200 -e BTARGET=bootloader BTYPE=release BOARD=WIPY
cp -v ports/cc3200/bootmgr/build/WIPY/release/bootloader.bin ../../deploy/micropython/wipy/bootloader-$mpyversion-p$prometheus_version-$mpybuilddate.bin
cc3200-make -C ports/cc3200 -e BTARGET=application BTYPE=release BOARD=WIPY
cp -v ports/cc3200/build/WIPY/release/mcuimg.bin ../../deploy/micropython/wipy/mcuimg-$mpyversion-p$prometheus_version-$mpybuilddate.bin
# Copy with overwrite, or symlink:
cp -vf ports/cc3200/build/WIPY/release/mcuimg.bin ../../deploy/micropython/wipy/mcuimg.bin
#unlink ../../deploy/micropython/wipy/mcuimg.bin || true
#ln -s ../../deploy/micropython/wipy/mcuimg-$mpyversion-p$prometheus_version-$mpybuilddate.bin ../../deploy/micropython/wipy/mcuimg.bin
