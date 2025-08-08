#!/bin/bash
# for local install
# dir_software=${HOME}/Software

# for docker install
dir_software=/app/Software
num_threads=16

apt-get -y remove cmake
apt-get -y purge cmake
apt-get -y autoremove
apt-get -y install libssl-dev build-essential
mkdir -p "${dir_software}"/cmake
cd "${dir_software}"/cmake || exit
wget -nc https://github.com/Kitware/CMake/releases/download/v4.0.3/cmake-4.0.3.tar.gz
# wget -nc https://github.com/Kitware/CMake/releases/download/v3.31.0/cmake-3.31.0.tar.gz
# wget -nc https://github.com/Kitware/CMake/releases/download/v3.29.3/cmake-3.29.3.tar.gz
tar -xf cmake-4.0.3.tar.gz
mkdir -p build
rm -rf build/*
cd build || exit
../cmake-4.0.3/bootstrap
make -j"${num_threads}" install
