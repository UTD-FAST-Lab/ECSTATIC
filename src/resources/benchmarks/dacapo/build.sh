#!/bin/bash

# Clone repository
CUR=$(pwd)
cd /
wget https://sourceforge.net/projects/dacapobench/files/9.12-bach-MR1/dacapo-9.12-MR1-bach.jar/download
mkdir /benchmarks
mkdir /download_temp
mv ./download ./download_temp
cd download_temp
unzip download
mv ./jar ../benchmarks/dacapo
cd /
rm -r download_temp