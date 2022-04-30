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
import logging
p = argparse.ArgumentParser('Tool to check whether partial orders were violated.')
p.add_argument("tool", choices=['flowdroid','droidsafe','amandroid'])
p.add_argument("benchmark", choices=['droidbench', 'test'])
p.add_argument('-j', '--jobs', default=8, type=int)
p.add_argument('--verbosity', '-v', action='count', default=0)
p.add_argument("file")
p.add_argument("output")
args = p.parse_args()

if args.verbosity < 1:
    logging.basicConfig(level=logging.CRITICAL)
elif args.verbosity == 1:
    logging.basicConfig(level=logging.WARNING)
elif args.verbosity == 2:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

from functools import partial
from multiprocessing import Pool
from src.checkmate.models.Tool import Tool
from csv import DictReader, DictWriter
import pickle
from typing import Dict, List

timeouts = {'droidbench': 600000,
           'test': 7200000}
defaults = {'flowdroid': 'config_FlowDroid_aplength5.xml',
            'droidsafe': 'config_DroidSafe_kobjsens3.xml',
            'amandroid': 'config_Amandroid_default.xml'}
def main():

    # First, read in the csv file that was passed in.
    records = list()
    logging.debug(f"Reading in file {args.file}")
    with open(args.file, encoding='utf-8-sig') as f:
        d = DictReader(f)
        [records.append(r) for r in d]
    logging.debug(f"Done reading in file. {len(records)} records found.")

    with open(f'data/{args.tool}.model', 'rb') as f:
        model : Tool = pickle.load(f)
    logging.debug("Checking model constraints now.")
    p = partial(compute_violations, records)
    results = list()
    with Pool(args.jobs) as pool:
        results = pool.map(p, model.options)
    all_results = list()
    [all_results.extend(r) for r in results]
    logging.debug(f"all_results: {all_results}")
    # all results is a list of tuples
    with open(args.output, 'w') as o:
        try:
            dw = DictWriter(o, fieldnames=all_results[0][0].keys())
            dw.writeheader()
            blank = {k: "" for k, v in all_results[0][0].items()}
            for a in all_results:
                dw.writerow(a[0])
                dw.writerow(a[1])
                dw.writerow(blank)
        except IndexError:
            print('No results to print.')
            


def compute_violations(records, o) -> List:
    logging.info(f'Checking violations for {o.name}')
    results = list()
    for model_list, compare_levels, compare_tp_fp_fn, relation_name in \
            [(o.precision, o.precision_compare, lambda x, y: x['fp'] <= y['fp'], 'precision'),
             (o.soundness, o.soundness_compare, lambda x, y: x['fn'] <= y['fn'], 'soundness')]:
        logging.debug(f'model_list = {model_list}')
        if len(model_list) > 0:
            if args.benchmark == 'droidbench':
                for r1 in records:
                    if num_timeouts(r1, records, args.benchmark) > 0:
                        continue
                    # If r1 is the default config
                    candidates = [r for r in records if r['generating_script'] != r1['generating_script'] and
                                  r['apk'] == r1['apk'] and
                                  (r['option_under_investigation'] == r1['option_under_investigation'] or
                                   defaults[args.tool] in r['generating_script'] or
                                   defaults[args.tool] in r1['generating_script']) and
                                  r['true_positive'] == r1['true_positive'] and
                                  r['replication'] == r1['replication']]
                    logging.debug(f'r1 = {r1}, candidates = {candidates}')
                    for r2 in candidates:
                        r1_option = r1['option_under_investigation']
                        r2_option = r2['option_under_investigation']
                        logging.debug(f'Comparing {r1_option}:{r1[r1_option]} to {r2_option}:{r2[r2_option]}')
                        if num_timeouts(r2, records, args.benchmark) > 0:
                            logging.debug('exiting because of timeouts.')
                            continue
                        try:
                            if compare_levels(r1[o.name], r2[o.name]) > 0:
                                logging.debug(f'comparing on {relation_name} {r1} {r2} {compare_tp_fp_fn(r1, r2)}')
                                if not compare_tp_fp_fn(r1, r2):
                                    results.append((r2, r1))
                                    print(f'Violation {relation_name}: {o.name} values {r1[o.name]} {r2[o.name]} on {r1} and {r2}')
                                else:
                                    logging.debug(f'Satisfied: {o.name} values {r1[o.name]} {r2[o.name]} on {r1} and {r2}')
                            else:
                                logging.debug(f'{o.name}:{r1[o.name]} is not more precise/sound than {r2[o.name]}')
                        except ValueError as ve:
                            logging.warning(ve)
                            continue
                        except KeyError as ke:
                            logging.debug(f'Option {o.name} is not in this result set.')
                            continue
            else: # test
                for r1 in records:
                    if float(r1['time']) > timeouts['test']:
                        continue # timed out
                    for r2 in [r for r in records if r['generating_script'] != r1['generating_script'] and
                               r['apk'] == r1['apk'] and
                               (r['option_under_investigation'] == r1['option_under_investigation'] or
                                defaults[args.tool] in r['generating_script'] or
                                (True if defaults[args.tool] in r1['generating_script'] else False)) and
                               float(r['time']) < timeouts['test'] and
                               r['replication'] == r1['replication']]:
                        try:
                           if compare_levels(r1[o.name], r2[o.name]) > 0:
                               r1_dict = {'tp': int(r1['detected_TP']), 'fp': int(r1['detected_FP']),
                                          'fn': int(r1['total_TP']) - int(r1['detected_TP'])}
                               r2_dict = {'tp': int(r2['detected_TP']), 'fp': int(r2['detected_FP']),
                                          'fn': int(r2['total_TP']) - int(r2['detected_TP'])}
                               if not compare_tp_fp_fn(r1_dict, r2_dict):
                                    # Make sure it wasn't because of a timeout.
                                    results.append((r2, r1))
                                    print(f'Violation {relation_name}: {o.name} values {r1[o.name]} {r2[o.name]} on {r1} and {r2}')
                               else:
                                    logging.debug(f'Satisfied: {o.name} values {r1[o.name]} {r2[o.name]} on {r1} and {r2}')
                        except ValueError as ve:
                            logging.warning(ve)
                            continue
                        except KeyError as ke:
                            logging.debug(f'Option {o.name} is not in this result set.')
                            continue

                           
                
    return results

def num_timeouts(r1: Dict, records: list, benchmark: str) -> int:
    if 'num_timeouts' not in r1:
        r1['num_timeouts'] = len([r for r in records if equals(r, r1) and int(r['time']) > timeouts[benchmark]])
    return r1['num_timeouts']
                
def equals(r1: Dict, r2: Dict) -> bool:
    return r1['replication'] == r2['replication'] and \
                r1['generating_script'] == r2['generating_script'] and \
                r1['apk'] == r2['apk'] and \
                r1['true_positive'] == r2['true_positive']

def get_tp_fp_fn(record: Dict, records: List[Dict]) -> Dict:
    """
    Computes the number of true positives, false positives, and false negatives for the value.
    """
    if not set(['tp', 'fp', 'fn']).issubset(set(record.keys())):
        record['tp'] = 0
        record['fp'] = 0
        record['fn'] = 0
        for r in records:
            if equals(r, record):
                f = lambda x : True if x.lower() == 'true' else False
                record['tp'] += f(r['true_positive']) and f(r['successful'])
                record['fp'] += not (f(r['true_positive']) or f(r['successful']))
                record['fn'] += f(r['true_positive']) and not(f(r['successful']))
    rval = {'tp': int(record['tp']),
            'fp': int(record['fp']),
            'fn': int(record['fn'])}
    logging.debug(f'rval = {rval}')
    return rval


if __name__ == '__main__':
    main()

