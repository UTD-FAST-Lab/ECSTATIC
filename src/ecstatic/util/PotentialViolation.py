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
import logging
from typing import List, Dict, Iterable, Set, TypeVar, Tuple, Callable, Sized, Container, Optional, Collection

from src.ecstatic.models.Level import Level
from src.ecstatic.util.PartialOrder import PartialOrder, PartialOrderType
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob

T = TypeVar('T')

logger = logging.getLogger(__name__)


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
    def expected_diffs(self) -> Collection[T]:
        """
        Returns the expected differences, if any. For example, if this PotentialViolation has partial order
        P.a MST P.b, it would return any T that are in the results associated with P.a but not P.b.
        """
        if self._expected_diffs is None:
            logger.debug("Computing expected diffs.")
            match self.get_main_partial_order():
                case PartialOrder(_, PartialOrderType.MORE_PRECISE_THAN, _):
                    logger.debug("Main partial order is precision. Computing job2 minus job1")
                    self._expected_diffs = self.job2_minus_job1
                case PartialOrder(_, PartialOrderType.MORE_SOUND_THAN, _):
                    logger.debug("Main partial order is soundness. Computing job1 minus job2")
                    self._expected_diffs = self.job1_minus_job2
                case _: raise RuntimeError("Pattern matching partial order failed.")
        return self._expected_diffs

    def get_main_partial_order(self) -> PartialOrder:
        def pred(left: Level, right: Level) -> bool:
            return left in self.job1.job.configuration.values() and right in self.job2.job.configuration.values()

        match self.partial_orders:
            case PartialOrder(left=left, right=right, type=_, option=_) if pred(left, right):
                return self.partial_orders
            case (PartialOrder(left=left, right=right, type=_, option=_), _) if pred(left, right):
                return self.partial_orders[0]
            case (_, PartialOrder(left=left, right=right, type=_, option=_)) if pred(left, right):
                return self.partial_orders[1]
            case _:
                raise RuntimeError(f"Unable to find partial order for potential violation "
                                   f"with partial orders {self.partial_orders}")


    @property
    def violated(self):
        """
        We assume that, in the case of multiple partial orders, the first partial order will have the options
        in the same order as the passed in jobs.
        Returns
        -------

        """
        if self._violated is None:
            # We need to compute the violation.
            match self.get_main_partial_order():
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
            logger.info(f"Job1 has {len(job1_results)} results and job2 has {len(job2_results)} results.")
            self._job1_minus_job2 = frozenset(job1_results.difference(job2_results))
            self._job2_minus_job1 = frozenset(job2_results.difference(job1_results))
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
        self._job1_minus_job2: Container[T] = None
        self._job2_minus_job1: Container[T] = None
        self._expected_diffs: Container[T] = None

