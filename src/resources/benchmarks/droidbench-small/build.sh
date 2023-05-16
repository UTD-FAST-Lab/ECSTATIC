#!/bin/bash
apt install -y rename
CURDIR=$(pwd)
cd /
mkdir -p benchmarks
cd /benchmarks
git clone https://github.com/Pancax/droidbench_android_projects.git
cd droidbench_android_projects/ActivityLifecycle1
./build.sh
cd $CURDIR