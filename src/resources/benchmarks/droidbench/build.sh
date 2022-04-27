#!/bin/bash

apt install -y parallel
CURDIR=$(pwd)
cd /
git clone https://github.com/secure-software-engineering/DroidBench/tree/develop
mkdir -p /benchmarks/droidbench
find ./DroidBench/apk -maxdepth 1 -type d | grep -v InterAppCommunication | parallel mv -t ./benchmarks/droidbench
cd $CURDIR