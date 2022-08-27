
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
            case ['ECSTATIC_results', *rest]:
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
