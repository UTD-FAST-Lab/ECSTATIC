#!/bin/bash

# Clone repository
CUR=$(pwd)
cd /
git clone git@github.com:amordahl/CATS-Microbenchmark.git
cd /CATS-Microbenchmark/benchmarks/Reflection/TrivialReflection/TR1

# Build repo
mvn clean compile package

# Move outputs
mkdir -p /benchmarks/test
cp ./target/TR1.jar /benchmarks/test
cd "$CUR"