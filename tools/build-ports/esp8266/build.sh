#!/bin/bash
rm -rf esp-open-sdk && git clone --recursive https://github.com/hwinther/esp-open-sdk.git
cd esp-open-sdk && sudo docker build --build-arg MAKE_ARGS="VENDOR_SDK=2.1.0" -t ghcr.io/hwinther/lanot/esp-open-sdk:2.1.0 -f Dockerfile . 
sudo docker run --rm -it ghcr.io/hwinther/lanot/esp-open-sdk:2.1.0