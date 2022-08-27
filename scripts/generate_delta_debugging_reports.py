
import sys
from pathlib import Path
from typing import List


def generate_record(line: str) -> str:

    def get_filename_attributes(tokenized_filename: List[str]):
        match tokenized_filename:
            case ['ECSTATIC_results', *rest]:
                return f"{rest[0]},{rest[1]},{rest[2]},{get_filename_attributes(rest[3:])}"
            case [type, *rest] if type in ['HDD_ONLY', 'CDG+HDD']:
                return f"{type},{get_filename_attributes(rest[1:])}"
            case ["DIRECT", *rest]:
                return f"{'/'.join(rest[2:-3])},{rest[-3]}"

    line = Path(line).absolute()
    return get_filename_attributes(line.split('/'))


if __name__ == "__main__":
    map(print, map(generate_record, sys.stdin))