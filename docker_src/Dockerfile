FROM ubuntu:24.04
# FROM plastimatch:latest
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

COPY py_requirements.txt ${dir_software}/py_requirements.txt
RUN python3.13 -m pip install -r ${dir_software}/py_requirements.txt

COPY install_plastimatch.sh ${dir_software}/install_plastimatch.sh
RUN --mount=type=ssh bash ${dir_software}/install_plastimatch.sh

RUN mkdir -p ${dir_software}/plastimatch-brachyutils
COPY plastimatch-api.py ${dir_software}/plastimatch-brachyutils/plastimatch-api.py
COPY run_api.sh ${dir_software}/plastimatch-brachyutils/run_api.sh


