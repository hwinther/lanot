#!/usr/bin/env bash
sudo docker build -t ghcr.io/hwinther/lanot/gcc-arm-none-eabi:10.3-2021.10 -f Dockerfile .
sudo docker run --rm -it ghcr.io/hwinther/lanot/gcc-arm-none-eabi:10.3-2021.10