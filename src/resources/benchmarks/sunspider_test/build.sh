#!/bin/bash
#
# ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
#
# Copyright (c) 2022.
#
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
CURDIR=$(pwd)
mkdir -p /benchmarks/sunspider
cd /benchmarks/sunspider
wget https://chromium.googlesource.com/v8/deps/third_party/benchmarks/+archive/refs/heads/master/sunspider.tar.gz
tar xzvf sunspider.tar.gz
cd $CURDIR