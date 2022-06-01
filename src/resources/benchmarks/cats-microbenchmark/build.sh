#!/bin/bash

# Clone repository
CUR=$(pwd)
mkdir -p /benchmarks
cd /benchmarks
git clone https://github.com/amordahl/CATS-Microbenchmark.git
cd CATS-Microbenchmark

# Build repo
mvn clean compile package

cd "$CUR"