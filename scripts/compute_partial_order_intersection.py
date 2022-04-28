#  CheckMate: A Configuration Tester for Static Analysis
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

import argparse
import os

p = argparse.ArgumentParser()
p.add_argument('csv', help='specifies violation to partial order mapping, first column must uniquely identify a file')
p.add_argument('output', help='where to write partial order files.')
args = p.parse_args()

def main():
    # Construct map from csv
    partial_order_to_files = dict()
    with open(args.csv, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            #print(f'Line is {line}')
            toks = line.split(',')
            violation = toks[0]
            #print(f'Violation is {violation}')
            partial_order = toks[1]
            if partial_order not in partial_order_to_files:
                partial_order_to_files[partial_order] = None
            for fi in os.listdir('.'):
                if violation in fi and fi.endswith('.diff'):
                    with open(fi) as f_prime:
                        content = set([l.strip() for l in f_prime.readlines()])
                    if partial_order_to_files[partial_order] is None:
                        partial_order_to_files[partial_order] = content
                    else:
                        partial_order_to_files[partial_order] = partial_order_to_files[partial_order].intersection(content)
                        print(f"Size of intersection for {partial_order} after file {fi} is {len(partial_order_to_files[partial_order])}")

    # Compute intersection
    for po, content in partial_order_to_files.items():
        if content is None:
            continue
        if not os.path.exists(args.output):
            os.mkdir(args.output)
        with open(os.path.join(args.output, po), 'w') as f:
            f.writelines([f'{c}\n' for c in content])

if __name__ == '__main__':
    main()