import argparse

p = argparse.ArgumentParser()
p.add_argument('-d', '--directory', help='The directory of flowsets.')
p.add_argument('--failedmode', choices=['ONLY_FAULTY', 'BOTH'], default='BOTH')
args = p.parse_args()
import logging
logging.basicConfig(level=logging.DEBUG)

import os
from typing import Dict, List, Tuple
import json

"""
Given an APK and a configuration, return the file name that should be output by the coverage_wrapper.py script.
"""
def compose_file_name(apk: str, config: str) -> str:
    return f'$FILE_LOCATION/{apk}_{config}.$EXTENSION'


"""
Given a directory, extract the configuration that produced it.
Currently, just operates off of the name.
Returns config1, config2, type
"""
def extract_configuration(dir: str) -> Tuple[str, str, str]:
    # Now, extract the configuration from the directory name.
    dir = os.path.basename(dir)
    config1 = "_".join(dir.split('_')[0:2])
    config2 = "_".join(dir.split('_')[2:4])
    config2 = 'default' if 'default' in config2.lower() else config2
    type = dir.split('_')[-1]
    return (config1, config2, type)

"""
Given a flowset directory, finds the violations.

Returns a map: configuration to a pair of sets, failed and passed
"""
def find_violations(dir: str) -> Dict[str, Tuple[List[str], List[str]]]:
    results : Dict[str, Tuple[List, List]]
    for root, dirs, files in os.walk(dir):
        # Collect all files that end in xml.
        files_list : List[str] = [f for f in files if f.endswith('.xml')]

        if len(files_list) == 0:
            logging.debug(f'No files found in directory {root}')
            continue
        
        # Just grab prefixes -- the part before the index and extension.
        # File names are like flowset_violation-true_Button3.apk_0.xml
        # So prefixes are like flowset_violation-true_Button3.apk
        files_prefixes : List[str] = ['_'.join(f.split('_')[:-1]).replace('.apk', '') for f in files_list]

        # Construct a map of apks to whether a violation was found
        # Ex. {apk1: ['violation_true'], apk2: ['violation_true', 'violation_false']}
        apk_to_violations : Dict[str, List[str, str]] = {}
        for prefix in files_prefixes:
            apk_name = prefix.split('_')[-1]
            if apk_name not in apk_to_violations:
                apk_to_violations[apk_name] = []
            apk_to_violations[apk_name].append(prefix.split('_')[1])

        # Violations are the ones that did not have a violation-false detected.
        violations : List[str] = [k for k, v in apk_to_violations.items() if 'violation-false' not in v]
        logging.debug(f'{len(violations)} violations found in {root}')
        if len(violations) == 0:
            continue
        non_violations : List[str] = [k for k, v in apk_to_violations.items() if k not in violations]
        all_apks = []
        all_apks.extend(violations)
        all_apks.extend(non_violations)
        
        logging.info(f'violations for {dir} are {violations}')
        logging.info(f'non-violations for {dir} are {non_violations}')
        config1, config2, type = extract_configuration(root)
        if type == 'soundness':
            faulty = config1
            non_faulty = config2
        elif type == 'precision':
            non_faulty = config1
            faulty = config2

        passed : List[str] = []
        failed : List[str] = []
        other : List[str] = []
        pairs : Dict[str, str] = {compose_file_name(apk, faulty): compose_file_name(apk, non_faulty) for apk in all_apks}
        
        if args.failedmode == 'BOTH':
            failed.extend([compose_file_name(apk, f) for apk in violations for f in [faulty, non_faulty]])
            passed.extend([compose_file_name(apk, f) for apk in non_violations for f in [faulty, non_faulty]])
        else:
            failed.extend([compose_file_name(apk, faulty) for apk in violations])
            passed.extend([compose_file_name(apk,faulty) for apk in non_violations])
            other.extend([compose_file_name(apk, non_faulty) for apk in all_apks])

        object_to_output = {'passed': passed, 'failed': failed, 'other': other, 'pairs': pairs}
        with open(os.path.join(root, f'{os.path.basename(root)}.json'), 'w') as f:
            json.dump(object_to_output, f)
    
def main():
    find_violations(args.directory)

if __name__ == '__main__':
    main()
