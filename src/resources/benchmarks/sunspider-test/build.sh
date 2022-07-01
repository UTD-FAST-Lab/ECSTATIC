#!/bin/bash

CURDIR=$(pwd)
mkdir -p /benchmarks/sunspider
cd /benchmarks/sunspider
wget https://chromium.googlesource.com/v8/deps/third_party/benchmarks/+archive/refs/heads/master/sunspider.tar.gz
tar xzvf sunspider.tar.gz
cd $CURDIR