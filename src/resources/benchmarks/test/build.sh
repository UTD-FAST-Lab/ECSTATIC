#!/bin/bash

# Clone repository
CUR=$(pwd)
mkdir -p /benchmarks/test
cd /benchmarks/test
git clone git@github.com:amordahl/CATS-Microbenchmark.git
cd ./CATS-Microbenchmark/benchmarks/Reflection/TrivialReflection/TR1

# Build repo
mvn clean compile package

cd "$CUR"