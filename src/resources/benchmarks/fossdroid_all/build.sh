#!/bin/bash

# Clone repository
CUR=$(pwd)
mkdir -p /benchmarks
cd /benchmarks
git clone https://github.com/Pancax/fossdroid_apks.git
cd $CUR
