#!/bin/bash
#!/bin/bash
# for local install
# dir_software=${HOME}/Software

# for docker install
dir_software=/app/Software
num_threads=16

apt install -y plastimatch

# apt install -y install g++ make git cmake-curses-gui \
#   libblas-dev liblapack-dev libsqlite3-dev \
#   libdcmtk-dev libdlib-dev libfftw3-dev \
#   libinsighttoolkit5-dev \
#   libpng-dev libtiff-dev uuid-dev zlib1g-dev

# cd ${dir_software}
# git clone --recurse-submodules https://github.com/engerlab/plastimatch-brachyutils.git

# cd ${dir_software}/plastimatch-brachyutils/plastimatch || exit
# mkdir build
# cd build || exit

