#!/bin/bash

# Clone repository
apt install parallel ant unzip -y
CUR=$(pwd)
cd /
git clone https://bitbucket.org/yanniss/doop-benchmarks.git --depth 1
cd /doop-benchmarks/dacapo-2006
mkdir -p /benchmarks/dacapo-2006
find . -type f -name '*.jar' | parallel cp -t /benchmarks/dacapo-2006
cp /checkmate/src/resources/benchmarks/dacapo-2006/index.json /benchmarks/dacapo-2006

# Clone sources
cd /
wget https://sourceforge.net/projects/dacapobench/files/archive/2006-10-MR2/dacapo-2006-10-MR2-src.zip
mkdir dacapo-2006-10-MR2-src
unzip -d dacapo-2006-10-MR2-src dacapo-2006-10-MR2-src.zip
cd dacapo-2006-10-MR2-src/benchmarks
cp /checkmate/src/resources/benchmarks/dacapo-2006/build.xml .
ant sources

find . -type f -name "*.tar.gz" | parallel cp -t /benchmarks/dacapo-2006
find . -type f -name "*.zip" | parallel cp -t /benchmarks/dacapo-2006
find . -type f -name '*.jar' | parallel cp -t /benchmarks/dacapo-2006
find . -type f -name '*.tgz' | parallel cp -t /benchmarks/dacapo-2006
cd $CUR