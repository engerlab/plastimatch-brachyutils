FROM ubuntu:24.04

FROM simple-elastix:latest
ARG dir_software="/app/Software"
WORKDIR ${dir_software}
USER root
# Install required packages
RUN apt update && apt install -y zip unzip wget curl net-tools x11-apps\
    nano git openssh-client &&\
    mkdir -p /root/.ssh &&\
    ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY docker_src/repositories/install_cmake.sh ${dir_software}/install_cmake.sh
RUN --mount=type=ssh bash ${dir_software}/install_cmake.sh
 
COPY docker_src/repositories/install_python.sh ${dir_software}/install_python.sh
RUN --mount=type=ssh bash ${dir_software}/install_python.sh
 
# COPY install_simpleElastix.sh ${dir_software}/install_simpleElastix.sh
# RUN --mount=type=ssh bash ${dir_software}/install_simpleElastix.sh
# 
# COPY py_requirements.txt ${dir_software}/py_requirements.txt
# RUN python3.13 -m pip install -r ${dir_software}/py_requirements.txt

# for development. delete later
# COPY run_api.sh ${dir_software}/SimpleElastix-brachyutils/run_api.sh
COPY elastix-api.py ${dir_software}/SimpleElastix-brachyutils/elastix-api.py

# RUN apt-get update && apt-get install -y \
    # build-essential cmake git \
    # libboost-all-dev libssl-dev \
    # libzmq3-dev pkg-config \
    # python3 python3-pip \
    # python3-setuptools python3-wheel \
    # wget libdcmtk-dev libdlib-dev libfftw3-dev \
    # libinsighttoolkit5-dev \
    # libpng-dev libtiff-dev uuid-dev zlib1g-dev \
    # plastimatch && \
    # apt-get clean && \
    # rm -rf /var/lib/apt/lists/*
# 
# RUN apt-get install pipx
# RUN pip3 install --break-system-packages pyplastimatch
# RUN python3 -c 'from pyplastimatch.utils.install import install_precompiled_binaries; install_precompiled_binaries()'

# ENTRYPOINT ["plastimatch"]



