import argparse
import json
import re

p = argparse.ArgumentParser()
p.add_argument("files", nargs="+")
args = p.parse_args()


def main():
    benchmark_sample = set()
    partial_order_sample = set()
    total_benchmarks = 0
    total_partial_orders = 0
    for fi in args.files:
        with open(fi) as f:
            record = json.load(f)
        for bs in record['benchmarks_sample']:
            san = re.search(r"name='(.*)'", bs).group(1)
            print(f"Sanitized {bs} to {san}")
            benchmark_sample.update(san)
        for po in record['partial_order_sample']:
            san = re.sub(r"(\d.*)", "",  po)
            print(f"Sanitized {po} to {san}")
            partial_order_sample.update(san)
        total_benchmarks = max(total_benchmarks, len(record['benchmarks']))
        total_partial_orders = max(total_partial_orders, len(record['partial_orders'].keys()))

    print(f"Number of benchmarks: {len(benchmark_sample)}/{total_benchmarks}")
    print(f"Number of partial orders: {len(partial_order_sample)}/{total_partial_orders}")

if __name__ == '__main__':
    main()
