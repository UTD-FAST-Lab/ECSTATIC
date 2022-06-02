#!/bin/bash
apt install -y rename
CURDIR=$(pwd)
cd /
mkdir -p benchmarks
cd /benchmarks
git clone https://github.com/Pancax/droidbench_android_projects.git
mkdir one_droid
mv droidbench_android_projects/ActivityEventSequence2 one_droid
mv droidbench_android_projects/build-all.sh one_droid
cd one_droid
./build-all.sh
cd $CURDIR