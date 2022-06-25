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
from typing import List, Dict, Iterable, Set, TypeVar, Tuple, Callable

from src.ecstatic.util.PartialOrder import PartialOrder, PartialOrderType
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob

T = TypeVar('T')


class PotentialViolation:

    def __eq__(self, o: object) -> bool:
        return isinstance(o, PotentialViolation) and self.violated == o.violated \
               and self.partial_orders == o.partial_orders and \
               frozenset([self.job1.results_location, self.job2.results_location]) == \
               frozenset([o.job1.results_location, o.job2.results_location])

    def __hash__(self) -> int:
        return hash((self.violated, self.partial_orders,
                     frozenset([self.job1.results_location, self.job2.results_location])))

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
                }

    def get_option_under_investigation(self):
        if self.job1.job.option_under_investigation is None:
            return self.job2.job.option_under_investigation
        else:
            return self.job1.job.option_under_investigation

    def is_transitive(self) -> bool:
        for p in self.partial_orders:
            if p.is_transitive():
                return True
        return False

    @property
    def expected_diffs(self) -> Iterable[T]:
        """
        Returns the expected differences, if any. For example, if this PotentialViolation has partial order
        P.a MST P.b, it would return any T that are in the results associated with P.a but not P.b.
        """
        if self._expected_diffs is None:
            match PotentialViolation.__get_first_partial_order():
                case PartialOrder(_, PartialOrderType.MORE_PRECISE_THAN, _):
                    self._expected_diffs = self.job1_minus_job2
                case PartialOrder(_, PartialOrderType.MORE_SOUND_THAN, _):
                    self._expected_diffs = self.job2_minus_job1
        return self._expected_diffs

    def __get_first_partial_order(self):
        match self.partial_orders:
            case (p1, _):
                return p1
            case PartialOrder(_, _, _, _):
                return self.partial_orders
            case _:
                raise RuntimeError("Can only compute violations on one partial order or a tuple of partial "
                                   "orders.")

    @property
    def violated(self):
        """
        We assume that, in the case of multiple partial orders, the first partial order will have the options
        in the same order as the passed in jobs. In other words,
        Returns
        -------

        """
        if self._violated is None:
            # We need to compute the violation.
            match PotentialViolation.__get_first_partial_order():
                case PartialOrder(_, PartialOrderType.MORE_SOUND_THAN, _, _):
                    self._violated = len(self.job2_minus_job1) > 0
                case PartialOrder(_, PartialOrderType.MORE_PRECISE_THAN, _, _):
                    self._violated = len(self.job1_minus_job2) > 0
                case _:
                    raise RuntimeError(f"Trying to compute violation with invalid partial order set "
                                       f"{self.partial_orders}")
        return self._violated

    @property
    def job2_minus_job1(self):
        # Force evaluation of the property for job1_minus_job2, so we don't have to duplicate the code.
        if self.job1_minus_job2 is not None:
            return self._job2_minus_job1

    @property
    def job1_minus_job2(self):
        if self._job1_minus_job2 is None:
            job1_results = self.job1_reader()
            job2_results = self.job2_reader()
            self._job1_minus_job2 = job1_results.difference(job2_results)
            self._job2_minus_job1 = job2_results.difference(job1_results)
        return self._job1_minus_job2

    def __init__(self,
                 partial_orders: PartialOrder | Tuple[PartialOrder, PartialOrder],
                 job1: FinishedFuzzingJob,
                 job2: FinishedFuzzingJob,
                 job1_reader: Callable[[], Set[T]],
                 job2_reader: Callable[[], Set[T]]):
        self._violated: bool | None = None
        self.partial_orders: PartialOrder | Tuple[PartialOrder, PartialOrder] = partial_orders
        self.job1 = job1
        self.job2 = job2
        self.job1_reader = job1_reader
        self.job2_reader = job2_reader
        self._job1_minus_job2: None | Iterable[T] = None
        self._job2_minus_job1: None | Iterable[T] = None
        self._expected_diffs: None | Iterable[T] = None
