#!/usr/bin/env bash
sudo docker build -t ghcr.io/hwinther/lanot/mpy-cross:13 -f Dockerfile .
sudo docker run --rm -it ghcr.io/hwinther/lanot/mpy-cross:13