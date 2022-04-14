#!/bin/bash

# Clone repository
apt install parallel -y
CUR=$(pwd)
cd /
git clone https://bitbucket.org/yanniss/doop-benchmarks.git --depth 1
cd /doop-benchmarks/dacapo-2006
mkdir /benchmarks/dacapo-2006
find . -type f -name '*.jar' | grep -v deps | parallel cp -t /benchmarks/dacapo-2006
