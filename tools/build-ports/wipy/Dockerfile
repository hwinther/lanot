FROM debian:13-slim AS base

LABEL maintainer="Hans Christian Winther-Sørensen <hwinther@gmail.com>"

WORKDIR /opt/sdk
ADD https://developer.arm.com/-/media/files/downloads/gnu-rm/10.3-2021.10/gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2?rev=78196d3461ba4c9089a67b5f33edf82a&revision=78196d34-61ba-4c90-89a6-7b5f33edf82a&hash=B94A380A17942218223CD08320496FB1 /opt/sdk/
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y bzip2 git python3 python3-setuptools make && \
    tar -xjf gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 && \
    rm gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/sdk/gcc-arm-none-eabi-10.3-2021.10/bin:${PATH}"

RUN git clone https://github.com/mon/cc3200tool.git
WORKDIR /opt/sdk/cc3200tool
RUN python3 setup.py install

ENTRYPOINT [ "arm-none-eabi-gcc", "--version" ]