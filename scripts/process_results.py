import json
import logging
import argparse
from typing import List, Dict
import os

p = argparse.ArgumentParser()
p.add_argument('results_file', help='The location of the results file.')
p.add_argument('output', help='where to write the output')
args = p.parse_args()


class ResultsProcessor:

    def __init__(self, results_file: str):
        self.results_file = results_file

    def get_lines_as_csv(self) -> List[Dict[str, str]]:
        with open(self.results_file) as f:
            lines = f.readlines()
        objs: List[Dict[str, str]] = [json.loads(x.strip()) for x in lines]

        csv = List[str]
        csv.append(','.join(objs[0].keys()) + '\n')
        [csv.append(','.join([val.replace(',', ';') for val in line.values()]) for line in objs + '\n')]
        return csv


if __name__ == '__main__':
    results_processor = ResultsProcessor(args.results_file)
    csv = results_processor.get_lines_as_csv()
    with open(args.output, 'w') as f:
        f.writelines(csv)
