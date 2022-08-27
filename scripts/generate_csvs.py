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
import os
from pathlib import Path
from typing import Iterable, List

p = argparse.ArgumentParser()
p.add_argument("directory")
args = p.parse_args()

def main():

    def find_all_violation_folders(root: Path) -> Iterable[Path]:
        for root, dirs, files in os.walk(root):
            for d in dirs:
                if d == 'violations':
                    yield Path(root) / d

    def find_all_violation_files(root: Path) -> Iterable[Path]:
        for root, dirs, files in os.walk(root):
            for f in files:
                if f.endswith('*.json'):
                    yield Path(root) / f

    def generate_comma_separated_record(file: Path) -> str:

        def reduce(tokens: List[str]) -> List[str]:
            match tokens:
                case ['violations', *rest]:
                    return ','.join(rest)
                case [head, *rest]:
                    return reduce(rest)

        return reduce(file)

    for folder in find_all_violation_folders(args.directory):
        for file in find_all_violation_files(folder):
            for line in generate_comma_separated_record(file):
                print(line)

if __name__ == "__main__":
    main()


