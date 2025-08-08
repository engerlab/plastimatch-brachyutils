#!/bin/bash
# for local install
# dir_software=${HOME}/Software

# for docker install
dir_software=/app/Software
num_threads=16

apt install -y build-essential zlib1g zlib1g-dev libncurses5-dev \
    libgdbm-dev pkg-config libnss3-dev libssl-dev libreadline-dev \
    libffi-dev libsqlite3-dev wget nano liblzma-dev libbz2-dev \
    libxrender1 libgl1 libglib2.0-0 tk-dev

# install python 3.13
cd ${dir_software} || exit
wget -nc https://www.python.org/ftp/python/3.13.3/Python-3.13.3.tgz
tar -xf Python-3.13.3.tgz
cd Python-3.13.3 || exit
./configure --enable-optimizations
make -j${num_threads}
make altinstall
echo alias python=python3.13 >>/etc/bash.bashrc
echo alias pip=pip3.13 >>/etc/bash.bashrc
source ${HOME}/.bashrc
python3.13 -m pip install --upgrade pip