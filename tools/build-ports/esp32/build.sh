#!/usr/bin/env bash
sudo docker build -t ghcr.io/hwinther/lanot/esp-idf-5:5.0.2 -f Dockerfile .
sudo docker run --rm -it --entrypoint idf.py ghcr.io/hwinther/lanot/esp-idf-5:5.0.2 --version