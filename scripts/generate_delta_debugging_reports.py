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
import sys
from pathlib import Path
from typing import List


def generate_record(line: str) -> str:

    def generate_info_from_file(file: Path) -> str:
        with open(file, 'r') as f:
            lines = f.readlines()

        def get_value(prefix: str) -> str:
            for l in lines:
                if l.startswith(prefix):
                    return l.split(' ')[-1].strip()

        start_line = get_value("start_line")
        end_line = get_value("end_line")
        total_reduction = (1 - (float(end_line)/float(start_line))) * 100
        binary_timer = get_value("binary_timer")
        hdd_timer = get_value("hdd_timer")
        program_timer = get_value("program_timer")
        return f"{start_line},{end_line},{total_reduction},{binary_timer},{hdd_timer},{program_timer}"

    def generate_csv_row(file_as_tokens: List[str]):
        match file_as_tokens:
            # Change 'results' to whatever your results folder is named.
            case ['results', *rest]:
                return f"{rest[0]},{rest[1]},{rest[2]},{generate_csv_row(rest[3:])}"
            case [type, *rest] if type in ['HDD_ONLY', 'CDG+HDD']:
                return f"{type},{generate_csv_row(rest[1:])}"
            case ["DIRECT", *rest]:
                return f"{'/'.join(rest[2:-3])},{rest[-3]}"
            case [_, *rest]:
                return generate_csv_row(rest)

    return f"{generate_csv_row(str(Path(line).absolute()).split('/'))},{generate_info_from_file(Path(line))}"


if __name__ == "__main__":
    for line in sys.stdin:
        print(generate_record(line.strip()))
