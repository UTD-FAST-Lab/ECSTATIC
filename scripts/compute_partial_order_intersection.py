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
                if violation in fi and fi.endswith('.classes.sorted'):
                    with open(fi) as f_prime:
                        content = set([l.strip() for l in f_prime.readlines()])
                    if partial_order_to_files[partial_order] is None:
                        partial_order_to_files[partial_order] = content
                    else:
                        partial_order_to_files[partial_order] = partial_order_to_files[partial_order].intersection(content)
                        print(f"Size of intersection for {partial_order} after file {fi} is {len(partial_order_to_files[partial_order])}")

    # Compute intersection
    for po, content in partial_order_to_files.items():
        if not os.path.exists(args.output):
            os.mkdir(args.output)
        with open(os.path.join(args.output, po), 'w') as f:
            f.writelines([f'{c}\n' for c in content])

if __name__ == '__main__':
    main()