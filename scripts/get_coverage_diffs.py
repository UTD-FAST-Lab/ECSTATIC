import argparse
import os
import subprocess
import time
import random

from checkmate.util import config

p = argparse.ArgumentParser()
p.add_argument('apk', help='apk to determine coverage of.')
p.add_argument('-s', '--script_location', help='where the shell scripts are located.')
p.add_argument('-c', '--coverage_location', help='coverage log location', default='./coverage')
p.add_argument('-f', '--force', help='overwrite records.', action='store_true')
p.add_argument('-d', '--diffs_location', help='where to store diffs', default='./diffs')
args = p.parse_args()

from typing import Tuple, List, Set
from pathlib import Path
import logging
logging.basicConfig(level=logging.DEBUG)


def get_config_name_from_apk_name(apk_name: str) -> Tuple[str, str]:
    # Example name is january_real_Threading_Looper1_7baaab9e231dd6adfa7d2d5ed04ed0e8_42c84347476d849c5186279326650631.apk
    toks = os.path.basename(apk_name).split('.')[0].split('_')
    shell = (toks[-2], toks[-1])
    logging.info(f'Shell is {shell}')
    return shell


def get_apk_name_from_apk_name(apk_name: str) -> Path:
    toks = apk_name.split('_')
    apk_name = f'{toks[-4]}_{toks[-3]}'
    logging.info(f'Apk name is {apk_name}')
    return apk_name


def main():
    # 1. Extract config hash from apk name.
    shell_1, shell_2 = get_config_name_from_apk_name(args.apk)

    # 2. Run each shell script
    outputfile1, outputfile2 = (run_script(args.apk, shell_1), run_script(args.apk, shell_2))

    # Get coverage sets
    coverage_set1, coverage_set2 = (read_coverage(outputfile1), read_coverage(outputfile2))

    logging.debug(f'Coverage set 1 contains {random.choices(list(coverage_set1), k=5)}')
    logging.debug(f'Coverage set 2 contains {random.choices(list(coverage_set2), k=5)}')
    # Write diff to file
    with open(os.path.join(args.diffs_location, f'{os.path.basename(args.apk)}.diff'), 'w') as f:
        diff = coverage_set1 - coverage_set2
        logging.debug(f'Size of diff is {diff}')
        f.writelines([f'{l}\n' for l in diff])


def read_coverage(output_file: str) -> Set[str]:
    with open(output_file, 'r') as f:
        return set([line.strip() for line in f.readlines() if line.startswith('COVERAGE:')])


def run_script(apk: str, script_location: str) -> str:
    output_location = os.path.join(args.coverage_location,
                                   f'{script_location.replace(".sh", "")}_{get_apk_name_from_apk_name(apk)}.coverage')
    if args.force or not os.path.exists(output_location):
        cmd = [os.path.join(args.script_location, script_location + ".sh"), "4", os.path.abspath(apk), config.configuration['android_platforms_location'],
               output_location]
        start = time.time()
        logging.info(f'Cmd is {" ".join(cmd)}')
        subprocess.run(cmd)
        print(f'Time for {output_location} is {time.time() - start}')

    return output_location


if __name__ == '__main__':
    main()
