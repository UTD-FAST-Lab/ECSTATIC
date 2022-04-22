from typing import List, Dict, Union, Iterable, Set, TypeVar

from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
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

    def as_dict(self) -> Dict[str, Union[str, Dict[str, str], List[str]]]:
        return {'violated': self.violated,
                'partial_orders': self.partial_orders,
                'job1': {
                    'config': [(str(k), str(v)) for k, v in self.job1.job.configuration.items()],
                    'result': self.job1.results_location
                },
                'job2': {
                    'config': [(str(k), str(v)) for k, v in self.job2.job.configuration.items()],
                    'result': self.job2.results_location
                },
                'target': self.job1.job.target.name,
                'differences': sorted(self.differences)
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
