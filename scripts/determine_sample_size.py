import argparse
import json
import re
from statistics import mean

p = argparse.ArgumentParser()
p.add_argument("files", nargs="+")
args = p.parse_args()


def main():
    benchmark_sample = dict()
    partial_order_sample = dict()
    total_benchmarks = 0
    total_partial_orders = 0
    for fi in args.files:
        with open(fi) as f:
            record = json.load(f)
        for bs in record['benchmarks_sample']:
            san = re.search(r"name='(.*?)'", bs).group(1)
            if san not in benchmark_sample:
                benchmark_sample[san] = 0
            benchmark_sample[san] += 1
        for po in record['partial_order_sample']:
            san = re.sub(r"(\d.*)", "",  po)
            if san not in partial_order_sample:
                partial_order_sample[san] = 0
            partial_order_sample[san] += 1

        total_benchmarks = max(total_benchmarks, len(record['benchmarks']))
        total_partial_orders = max(total_partial_orders, len(record['partial_orders'].keys()))

    print(f"Number of benchmarks: {len(benchmark_sample.keys())}/{total_benchmarks}")
    print(f"Sampling ranged from {min(benchmark_sample.values())} to {max(benchmark_sample.values())} (mean {mean(benchmark_sample.values())}")
    print(f"Number of partial orders: {len(partial_order_sample)}/{total_partial_orders}")
    print(f"Sampling ranged from {min(partial_order_sample.values())} to {max(partial_order_sample.values())} (mean {mean(partial_order_sample.values())}")


if __name__ == '__main__':
    main()
