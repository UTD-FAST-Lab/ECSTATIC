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

from typing import List, Dict, Iterable, Set, TypeVar, Tuple

from src.checkmate.util.PartialOrder import PartialOrder
from src.checkmate.util.UtilClasses import FinishedFuzzingJob

T = TypeVar('T')


class Violation:

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Violation) and self.violated == o.violated \
               and self.partial_orders == o.partial_orders and self.job1 == o.job1 \
               and self.job2 == o.job2 and self.differences == o.differences

    def __hash__(self) -> int:
        return hash((self.violated, self.partial_orders, self.job1, self.job2, self.differences))

    def as_dict(self) -> Dict[str, str | List[str] | List[Tuple[str]]]:
        return {'violated': self.violated,
                'partial_orders': [str(v) for v in self.partial_orders],
                'job1': {
                    'config': [(str(k), str(v)) for k, v in self.job1.job.configuration.items()],
                    'result': self.job1.results_location
                },
                'job2': {
                    'config': [(str(k), str(v)) for k, v in self.job2.job.configuration.items()],
                    'result': self.job2.results_location
                },
                'target': self.job1.job.target.name,
                'differences': sorted([str(d) for d in self.differences])
                }

    def get_option_under_investigation(self):
        if self.job1.job.option_under_investigation is None:
            return self.job2.job.option_under_investigation
        else:
            return self.job1.job.option_under_investigation

    def __init__(self, violated: bool, partial_orders: Set[PartialOrder],
                 job1: FinishedFuzzingJob, job2: FinishedFuzzingJob,
                 differences: Iterable[T]):
        self.violated = violated
        self.partial_orders = frozenset(partial_orders)
        self.job1 = job1
        self.job2 = job2
        self.differences = differences
