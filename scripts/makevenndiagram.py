#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


import matplotlib
import venn
import argparse

"""
Venn is from https://github.com/tctianchi/pyvenn
"""

p = argparse.ArgumentParser()
p.add_argument('files', nargs=5)
args = p.parse_args()

lines = list()
for f in sorted(args.files):
    with open(f, 'r') as infile:
        lines.append(infile.readlines())
        
labels = venn.get_labels(lines)
fig, ax = venn.venn5(labels, ['','','','',''])
matplotlib.pyplot.savefig('test.png')


