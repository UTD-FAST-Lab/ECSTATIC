#!/bin/bash
CURDIR=$(pwd)
cd /
mkdir -p benchmarks
cd /benchmarks
git clone https://github.com/Pancax/droidbench_android_projects.git
cd droidbench_android_projects
./script.sh
cd $CURDIR