#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
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
import os
from pathlib import Path
from typing import Iterable, Tuple, Set

from src.ecstatic.util.PartialOrder import PartialOrder, PartialOrderType
logging.basicConfig(level=logging.DEBUG)
p = argparse.ArgumentParser()
p.add_argument("directory", help="The violations directory")
args = p.parse_args()


def main():
    def get_json_files(directory: Path) -> Iterable[Path]:
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".json"):
                    logging.debug(f"Found file {Path(root) / Path(f)}")
                    yield Path(root) / Path(f)

    def parse_file_name(file: Path) -> Tuple[str, frozenset[str], str]:
        tokens = str(file.absolute()).split('/')
        benchmark = tokens[-1]
        second_po = tokens[-4:-1]
        first_po = tokens[-7:-4]
        logging.debug(f"First po is {first_po}")
        logging.debug(f"Second po is {second_po}")
        if first_po[1] not in ['MST', 'MPT']:
            logging.info(f"{file} only has one partial order.")
        else:
            option_name = tokens[-8]
            return option_name, frozenset({'/'.join(first_po), '/'.join(second_po)}), benchmark

    seen = {}
    to_delete = []

    def myjoin(strs: Iterable[str]):
        logging.debug("key is {strs}")
        return '/'.join(strs)

    for f in sorted(get_json_files(args.directory), key = lambda x: myjoin(str(x).split()[-8:])):
        fingerprint_tuple = parse_file_name(f)
        if fingerprint_tuple not in seen:
            seen[fingerprint_tuple] = f.absolute()
        else:
            logging.critical(f"{f} is a duplicate of {seen[fingerprint_tuple]}")
            to_delete.append(f)


if __name__ == '__main__':
    main()
