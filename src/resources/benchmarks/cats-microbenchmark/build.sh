#!/bin/bash

# Clone repository
CUR=$(pwd)
cd /
git clone git@github.com:amordahl/CATS-Microbenchmark.git
cd CATS-Microbenchmark

# Build repo
mvn clean compile package

# Move outputs
mkdir -p /benchmarks
rm -r /benchmarks/cats-microbenchmark
mv ./outputs /benchmarks/cats-microbenchmark
cd $CUR