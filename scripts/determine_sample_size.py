import argparse
import json

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
            benchmark_sample.update(bs)
        for po in record['partial_order_sample']:
            partial_order_sample.update(po)
        total_benchmarks = max(total_benchmarks, len(record['benchmarks']))
        total_partial_orders = max(total_partial_orders, len(record['partial_orders'].keys()))

    print(f"Number of benchmarks: {len(benchmark_sample)}/{total_benchmarks}")
    print(f"Number of partial orders: {len(partial_order_sample)}/{total_partial_orders}")

if __name__ == '__main__':
    main()
