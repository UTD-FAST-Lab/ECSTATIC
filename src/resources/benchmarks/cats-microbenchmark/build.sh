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
mkdir /benchmarks/cats-microbenchmark
find . type f -name '*.jar' -execdir mv '{}' -t /benchmark/cats-microbenchmark \;
cd "$CUR"