#!/bin/bash
#!/bin/bash
# for local install
# dir_software=${HOME}/Software

# for docker install
dir_software=/app/Software
num_threads=16

# apt install -y build-essential

cd ${dir_software}
git clone --recurse-submodules https://github.com/engerlab/SimpleElastix-brachyutils.git

cd ${dir_software}/SimpleElastix-brachyutils/SimpleITK || exit
mkdir build
cd build || exit

cmake ../SuperBuild -DSimpleITK_USE_ELASTIX=ON
    # -DSIMPLEITK_USE_PYTHON=ON \
    # -DSIMPLEITK_USE_PYTHON_WRAPPING=ON

make -j ${num_threads}
python3.13 -m pip install SimpleITK-build/Wrapping/Python