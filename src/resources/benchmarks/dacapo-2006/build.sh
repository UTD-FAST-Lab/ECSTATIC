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