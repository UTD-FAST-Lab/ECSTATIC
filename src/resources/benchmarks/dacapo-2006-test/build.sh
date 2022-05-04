#!/bin/bash

# Clone repository
apt install parallel ant javacc unzip -y
CUR=$(pwd)
mkdir -p /benchmarks
cd /benchmarks
git clone https://github.com/amordahl/Dacapo-2006.git
cd Dacapo-2006/benchmarks/build_scripts
find . -type f -name '*.sh' -exec {} \;
cd $CUR