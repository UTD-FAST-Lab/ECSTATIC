#!/bin/bash

# Clone repository
CUR=$(pwd)
mkdir -p /benchmarks/test
cd /benchmarks/test
git clone https://github.com/amordahl/CATS-Microbenchmark.git
cd ./CATS-Microbenchmark/benchmarks/Unsafe/Unsafe1

# Build repo
mvn clean compile package

cd "$CUR"