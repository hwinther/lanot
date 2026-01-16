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
export mpyversion=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_GIT_TAG | cut -d' ' -f3 | cut -d'"' -f2`
export mpybuilddate=`cat mpy-cross/build/genhdr/mpversion.h | grep MICROPY_BUILD_DATE | cut -d' ' -f3 | cut -d'"' -f2`
export prometheus_version=`cat ../../src/core/prometheus/__init__.py | grep __version__ | cut -d"'" -f2`

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp8266 $mpyversion-$prometheus_version-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
esp8266-make() {
    sudo docker run --rm -v $(pwd)/../../:/opt/lanot -w /opt/lanot/tools/micropython --entrypoint bash ghcr.io/hwinther/lanot/esp-open-sdk:2.1.0 -c "set -x && git config --global --add safe.directory '*' && make $*"
}
esp8266-make -C ports/esp8266 submodules
esp8266-make -C ports/esp8266 -j BOARD=NODEMCUESP12E
cp -v ports/esp8266/build-NODEMCUESP12E/firmware-combined.bin ../../deploy/micropython/esp8266/NODEMCUESP12E-$mpyversion-$prometheus_version-$mpybuilddate.bin
esp8266-make -C ports/esp8266 -j BOARD=LOLINESP32E
cp -v ports/esp8266/build-LOLINESP32E/firmware-combined.bin ../../deploy/micropython/esp8266/LOLINESP32E-$mpyversion-$prometheus_version-$mpybuilddate.bin

# Temporary hack, later all SDKs should use the same debian version
#mpy-make -C mpy-cross clean
mpy-make -C mpy-cross MICROPY_PY_FUNCTION_ATTRS=1
# /hack

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making esp32 $mpyversion-$prometheus_version-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
esp32-make() {
    local BOARD=${1:-NODEMCU32S}
    sudo docker run --rm -v $(pwd)/../../:/opt/lanot -w /opt/lanot -e IDF_PATH=/opt/sdk/esp-idf --entrypoint bash --privileged -u 0 ghcr.io/hwinther/lanot/esp-idf-5:5.0.2 -c "set -x && cp -rd /opt/lanot/tools/micropython /opt/micropython && cd /opt/micropython/ports/esp32 && cp /opt/lanot/tools/prometheus.micropython.manifest.py /opt/ && make -j BOARD=$BOARD && mkdir -p /opt/lanot/tools/micropython/ports/esp32/build-${BOARD}/ && cp /opt/micropython/ports/esp32/build-${BOARD}/firmware.bin /opt/lanot/tools/micropython/ports/esp32/build-${BOARD}/"
}
make -C ports/esp32 submodules
esp32-make NODEMCU32S
cp -v ports/esp32/build-NODEMCU32S/firmware.bin ../../deploy/micropython/esp32/NODEMCU32S-$mpyversion-$prometheus_version-$mpybuilddate.bin

printf "${BLUE}*******************************************${NC}\n"
printf "${BLUE}* Making cc3200-WIPY $mpyversion-$prometheus_version-$mpybuilddate *${NC}\n"
printf "${BLUE}*******************************************${NC}\n"
cc3200-make() {
    sudo docker run --rm -v $(pwd)/../../:/opt/lanot -w /opt/lanot/tools/micropython --entrypoint make ghcr.io/hwinther/lanot/gcc-arm-none-eabi:10.3-2021.10 "$@"
}
cc3200-make -C ports/cc3200 -e BTARGET=bootloader BTYPE=release BOARD=WIPY
cp -v ports/cc3200/bootmgr/build/WIPY/release/bootloader.bin ../../deploy/micropython/wipy/bootloader-$mpyversion-$prometheus_version-$mpybuilddate.bin
cc3200-make -C ports/cc3200 -e BTARGET=application BTYPE=release BOARD=WIPY
cp -v ports/cc3200/build/WIPY/release/mcuimg.bin ../../deploy/micropython/wipy/mcuimg-$mpyversion-$prometheus_version-$mpybuilddate.bin
# Copy with overwrite, or symlink:
cp -fv ports/cc3200/build/WIPY/release/mcuimg.bin ../../deploy/micropython/wipy/mcuimg.bin
#unlink ../../deploy/micropython/wipy/mcuimg.bin || true
#ln -s ../../deploy/micropython/wipy/mcuimg-$mpyversion-$prometheus_version-$mpybuilddate.bin ../../deploy/micropython/wipy/mcuimg.bin
