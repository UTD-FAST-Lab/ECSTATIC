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


