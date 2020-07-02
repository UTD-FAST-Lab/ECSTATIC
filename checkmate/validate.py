from tqdm import tqdm
from functools import partial
from multiprocessing import Pool
from checkmate.models.Constraint import Constraint
from checkmate.models.Option import Option
from checkmate.models.Level import Level
from checkmate.models.Tool import Tool
from csv import DictReader, DictWriter
import pickle
import logging
from typing import Dict, Tuple, List

logging.basicConfig(level=logging.INFO)
import argparse
p = argparse.ArgumentParser('Tool to check whether partial orders were violated.')
p.add_argument("tool", choices=['flowdroid','droidsafe','amandroid'])
p.add_argument("benchmark", choices=['droidbench', 'fossdroid'])
p.add_argument("file")
args = p.parse_args()

timeouts: {'droidbench': 600000,
           'fossdroid': 7200000}
def main():

    # First, read in the csv file that was passed in.
    records = list()
    logging.debug(f"Reading in file {args.file}")
    with open(args.file, encoding='utf-8-sig') as f:
        d = DictReader(f)
        [records.append(r) for r in d]
    logging.debug(f"Done reading in file. {len(records)} records found.")

    with open(f'/Users/austin/PycharmProjects/checkmate/data/{args.tool}.model', 'rb') as f:
        model : Tool = pickle.load(f)
    logging.debug("Checking model constraints now.")
    p = partial(compute_violations, records)
    with Pool(8) as pool:
        pool.map(p, model.options)


def compute_violations(records, o):
    logging.info(f'Checking violations for {o.name}')
    for model_list, compare_levels, compare_tp_fp_fn in \
            [(o.precision, o.precision_compare, lambda x, y: x['fp'] <= y['fp']),
             (o.soundness, o.soundness_compare, lambda x, y: x['fn'] <= y['fn'])]:
        if len(model_list) > 0:
            for r1 in tqdm(records):
                for r2 in [r for r in records if r['generating_script'] != r1['generating_script']]:
                    try:
                        if compare_levels(r1[o.name], r2[o.name]) > 0:
                            if not compare_tp_fp_fn(get_tp_fp_fn(r1, records), get_tp_fp_fn(r2, records)):
                                # Make sure it wasn't because of a timeout.
                                if int(r1['time']) > timeouts[args.tool] or int(r2['time']) > timeouts[args.tool]:
                                       continue
                                print(f'Violation: {o.name} values {r1[o.name]} {r2[o.name]} on {r1} and {r2}')
                            else:
                                logging.debug(f'Satisfied: {r1} and {r2} on {o.name} values {r1[o.name]}, {r2[o.name]}')
                    except ValueError as ve:
                        logging.warning(ve)
                        continue
                    except KeyError as ke:
                        logging.debug(f'Option {o.name} is not in this result set.')
                        continue


def get_tp_fp_fn(record: Dict, records: List[Dict]) -> Dict:
    """
    Computes the number of true positives, false positives, and false negatives for the value.
    """
    if not set(['tp', 'fp', 'fn']).issubset(set(record.keys())):
        record['tp'] = 0
        record['fp'] = 0
        record['fn'] = 0
        for r in records:
            if r['replication'] == record['replication'] and \
                r['generating_script'] == record['generating_script'] and \
                r['apk'] == record['apk']:
                f = lambda x : True if x.lower() == 'true' else False
                record['tp'] += f(r['true_positive']) and f(r['successful'])
                record['fp'] += not (f(r['true_positive']) or f(r['successful']))
                record['fn'] += f(r['true_positive']) and not(f(r['successful']))
    return {'tp': record['tp'],
            'fp': record['fp'],
            'fn': record['fn']}


if __name__ == '__main__':
    main()

