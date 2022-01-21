import argparse
import os
import subprocess

from checkmate.util import config

p = argparse.ArgumentParser()
p.add_argument('apk', help='apk to determine coverage of.')
p.add_argument('-s', '--script_location', help='where the shell scripts are located.')
p.add_argument('-c', '--coverage_location', help='coverage log location', default='./coverage')
args = p.parse_args()

from typing import Tuple, List, Set
from pathlib import Path
import logging


def get_config_name_from_apk_name(apk_name: str) -> Tuple[Path, Path]:
    raise NotImplementedError


def get_apk_name_from_apk_name(apk_name: str) -> Path:
    raise NotImplementedError


def main():
    # 1. Extract config hash from apk name.
    shell_1, shell_2 = get_config_name_from_apk_name(args.apk)

    # 2. Run each shell script
    outputfile1, outputfile2 = (run_script(args.apk, shell_1), run_script(args.apk, shell_2))

    # Get coverage sets
    coverage_set1, coverage_set2 = (read_coverage(outputfile1), read_coverage(outputfile2))

    # Write diff to file
    with open(f'{args.apk}.diff', 'w') as f:
        f.writelines(list(coverage_set1.difference(coverage_set2)))


def read_coverage(output_file: str) -> Set[str]:
    with open(output_file, 'r') as f:
        return set([line.strip() for line in f.readlines() if line.startswith('COVERAGE:')])


def run_script(apk: str, script_location: str) -> Path:
    output_location = os.path.join(args.coverage,
                                   f'{script_location.replace(".sh", "")}_{get_apk_name_from_apk_name(apk)}.coverage')
    if not os.path.exists(output_location):
        cmd = [script_location, "4", os.path.abspath(apk), config.configuration['android_platforms_location'],
               output_location]
        subprocess.run(cmd)

    return output_location


if __name__ == '__main__':
    main()
