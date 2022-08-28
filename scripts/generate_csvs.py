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
import sys
from pathlib import Path
from typing import Iterable, List
def main(file: str):

    def find_all_violation_files(root: Path) -> Iterable[Path]:
        for root, dirs, files in os.walk(root):
            for f in files:
                if f.endswith('.json'):
                    yield Path(root) / f

    def generate_comma_separated_record(file: Path) -> str:

        def reduce1(tokens: List[str]) -> str:
            match tokens:
                case ['ECSTATIC_results', *rest]:
                    return f"{rest[0]},{rest[1]},{reduce(rest)}"
                case [_, *rest]:
                    return reduce1(rest)

        def reduce(tokens: List[str]) -> str:
            match tokens:
                case [head, *rest] if head.startswith('campaign'):
                    return f"{head},{reduce(rest)}"
                case ['violations', *rest]:
                    return ','.join([*rest[:4], '/'.join(rest[4:-1]), rest[-1]])
                case [head, *rest]:
                    return reduce(rest)

        return reduce1(str(file).split('/'))

    return generate_comma_separated_record(Path(file).absolute()).strip()

if __name__ == "__main__":
    for file in sys.stdin:
        print(main(file))


