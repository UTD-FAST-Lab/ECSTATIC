#!/bin/bash

apt install -y parallel
CURDIR=$(pwd)
cd /
git clone https://github.com/secure-software-engineering/DroidBench.git
cd DroidBench
git checkout develop
mkdir -p /benchmarks/droidbench
find ./apk -maxdepth 1 -type d | grep -v InterAppCommunication | parallel mv -t /benchmarks/droidbench
cd /benchmarks/droidbench
cd $CURDIR