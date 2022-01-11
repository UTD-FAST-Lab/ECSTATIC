import json
import logging
import argparse
import re
from typing import List, Dict, Set
import os

p = argparse.ArgumentParser()
p.add_argument('results_file', help='The location of the results file.')
p.add_argument('output', help='where to write the output')
args = p.parse_args()


class ResultsProcessor:

    def __init__(self, results_file: str):
        self.results_file = results_file

    def get_lines_as_csv(self) -> List[str]:
        with open(self.results_file) as f:
            lines = f.readlines()
        objs: List[RunRecord] = [RunRecord(json.loads(x.strip())) for x in lines]
        # add apk in if it doesn't exist
        for o in objs:
            if 'apk' not in o.record:
                apk = re.search(r"[\w\d_]+\.apk", o.record['results'][0]).group(0)
                o.record['apk'] = apk

        for o in objs:
            option = o.record['option_under_investigation'][0]
            if 'partial_order' not in o.record:
                partial_order = f'{option}:{o.record["config1"][option]} {o.record["relation"]} {option}:{o.record["config2"][option]}'
                o.record['partial_order'] = partial_order

        objs = list(sorted(objs, key=lambda x: x.record['start_time']))
        objs_set: Set[RunRecord] = set()
        for r in objs:
            if r not in objs_set:
                objs_set.add(r)
            else:
                equals = [l for l in objs_set if l == r]
                pass
        #     [objs_set.add(r) for r in objs]

        objs = list(objs_set)
        csv: List[str] = list()
        csv.append(','.join(objs[0].record.keys()) + '\n')
        [csv.append(','.join([str(val).replace(',', ';') for val in line.record.values()]) + '\n') for line in objs_set]
        return csv


class RunRecord:
    def __init__(self, record: Dict[str, str]):
        self.record = record

    relevant_fields: List[str] = ['option_under_investigation', 'type']

    def __eq__(self, other):
        if not isinstance(other, RunRecord):
            return False

        for field in RunRecord.relevant_fields:
            if self.record[field] != other.record[field]:
                return False

        option: str = self.record['option_under_investigation'][0]
        for config in ['config1', 'config2']:
            if self.record[config][option] != other.record[config][option]:
                return False

        return True

    def __hash__(self):
        items_to_hash = list()
        for field in RunRecord.relevant_fields:
            if isinstance(self.record[field], List):
                items_to_hash.extend(self.record[field])
            else:
                items_to_hash.append(self.record[field])
        for config in ['config1', 'config2']:
            items_to_hash.append(self.record[config][self.record['option_under_investigation'][0]])
        return hash(tuple(items_to_hash))


if __name__ == '__main__':
    results_processor = ResultsProcessor(args.results_file)
    csv = results_processor.get_lines_as_csv()
    with open(args.output, 'w') as f:
        f.writelines(csv)
