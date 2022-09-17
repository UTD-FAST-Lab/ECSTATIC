#!/bin/bash

CUR = $(pwd)
mkdir /benchmarks
cd /benchmarks
git clone https://github.com/jquery/jquery.git
cd jquery
git checkout 1.11.0
cd $CUR
