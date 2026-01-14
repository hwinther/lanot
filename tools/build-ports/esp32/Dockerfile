FROM debian:13-slim AS base

LABEL maintainer="Hans Christian Winther-Sørensen <hwinther@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git python3 python3-venv libbsd-dev libffi-dev libglib2.0-0 libncurses-dev libpixman-1-0 libgcrypt20 libsdl2-2.0-0 libslirp0 libusb-1.0-0-dev make cmake && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 13

FROM base AS esp-idf

WORKDIR /opt/sdk
# Micropython 1.20 - ESP-IDF v5.0.2
# Micropython 1.27 - ESP-IDF v5.5.1
ARG ESP_IDF_VERSION=v5.0.2
RUN git clone -b ${ESP_IDF_VERSION} --recursive https://github.com/espressif/esp-idf.git

WORKDIR /opt/sdk/esp-idf
# To reduce the image size, specify required platforms e.g. esp32 esp32s2 esp32s3 riscv32
ARG INSTALL_ARGS=""
RUN ./install.sh ${INSTALL_ARGS}

ARG IDF_INSTALL_TARGETS=all
ENV IDF_PATH=/opt/sdk/esp-idf

# Install all the required tools
RUN : \
  && update-ca-certificates --fresh \
  && $IDF_PATH/tools/idf_tools.py --non-interactive install required --targets=${IDF_INSTALL_TARGETS} \
  && $IDF_PATH/tools/idf_tools.py --non-interactive install qemu* --targets=${IDF_INSTALL_TARGETS} \
  && $IDF_PATH/tools/idf_tools.py --non-interactive install cmake \
  && $IDF_PATH/tools/idf_tools.py --non-interactive install-python-env \
  && rm -rf $IDF_TOOLS_PATH/dist \
  && :

# The constraint file has been downloaded and the right Python package versions installed. No need to check and
# download this at every invocation of the container.
ENV IDF_PYTHON_CHECK_CONSTRAINTS=no

RUN rm -rf /root/.espressif/dist/ /opt/sdk/esp-idf/.git

FROM base AS final
COPY --from=esp-idf /root/.espressif /root/.espressif
COPY --from=esp-idf /opt/sdk/esp-idf /opt/sdk/esp-idf

ENV PATH="/opt/sdk/esp-idf/components/espcoredump:\
/opt/sdk/esp-idf/components/partition_table:\
/opt/sdk/esp-idf/components/app_update:\
/root/.espressif/tools/xtensa-esp-elf-gdb/11.2_20220823/xtensa-esp-elf-gdb/bin:\
/root/.espressif/tools/riscv32-esp-elf-gdb/11.2_20220823/riscv32-esp-elf-gdb/bin:\
/root/.espressif/tools/xtensa-esp32-elf/esp-2022r1-11.2.0/xtensa-esp32-elf/bin:\
/root/.espressif/tools/xtensa-esp32s2-elf/esp-2022r1-11.2.0/xtensa-esp32s2-elf/bin:\
/root/.espressif/tools/xtensa-esp32s3-elf/esp-2022r1-11.2.0/xtensa-esp32s3-elf/bin:\
/root/.espressif/tools/riscv32-esp-elf/esp-2022r1-11.2.0/riscv32-esp-elf/bin:\
/root/.espressif/tools/esp32ulp-elf/2.35_20220830/esp32ulp-elf/bin:\
/root/.espressif/tools/openocd-esp32/v0.11.0-esp32-20221026/openocd-esp32/bin:\
/root/.espressif/python_env/idf5.0_py3.13_env/bin:\
/opt/sdk/esp-idf/tools:${PATH}"

# ENTRYPOINT [ "idf.py", "--version" ]
# If paths keep changing, consider using a script to set up the environment:
ENTRYPOINT ["/bin/bash", "-c", "source /opt/sdk/esp-idf/export.sh && exec \"$@\"", "--"]
CMD ["/bin/bash"]
