cd micropython
echo Making mpy cross compiler
make -C mpy-cross
cd esp8266
echo Making esp8266
make axtls
make && cp build/firmware-combined.bin ../../../build/micropython/esp8266/

echo Making cc3200-WIPY
cd ../cc3200
make BTARGET=bootloader BTYPE=release BOARD=WIPY && cp bootmgr/build/WIPY/release/bootloader.bin ../../../build/micropython/wipy/custom/
make BTARGET=application BTYPE=release BOARD=WIPY && cp build/WIPY/release/mcuimg.bin ../../../build/micropython/wipy/custom/
