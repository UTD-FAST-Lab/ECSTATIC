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
from typing import Iterable, Tuple

from src.ecstatic.debugging.AbstractDeltaDebugger import DeltaDebuggingPredicate, GroundTruth
from src.ecstatic.debugging.BenchmarkDeltaDebugger import BenchmarkDeltaDebugger
from src.ecstatic.debugging.JavaDeltaDebugger import JavaDeltaDebugger
from src.ecstatic.util.PartialOrder import PartialOrderType
from src.ecstatic.util.PotentialViolation import PotentialViolation

logger = logging.getLogger(__name__)


class JavaBenchmarkDeltaDebugger(BenchmarkDeltaDebugger, JavaDeltaDebugger):
    def make_predicates(self, potential_violation: PotentialViolation) -> Iterable[Tuple[DeltaDebuggingPredicate, GroundTruth]]:
        """
        Returns the predicates and ground truths for a potential violation. If the potential violation's main
        partial order (i.e., in the case that there are two potential partial order violations, we want the partial
        order that matches the order of the jobs, such that job1 has some relationship to job2).
        :param potential_violation: The non-violation
        :return:
        """
        mp = potential_violation.get_main_partial_order()
        if (not potential_violation.is_violation) and (len(potential_violation.expected_diffs) > 0) and \
            mp.is_explicit():
            match mp.type:
                case PartialOrderType.MORE_SOUND_THAN:
                    # If it's a soundness partial order, then we are not sure how many of the additional edges
                    #  produces by the more sound configuration
                    def predicate(pv: PotentialViolation):
                        return pv.expected_diffs <= potential_violation.expected_diffs
                    ground_truth = {
                        "partial_order": str(mp),
                        "left_preserve_at_least_one": [str(e) for e in potential_violation.expected_diffs]
                    }
                    yield predicate, ground_truth
                case PartialOrderType.MORE_PRECISE_THAN:
                    # If it's a precision partial order, we create a new benchmark for each of the edges missing in the
                    #  more precise result, since we can be confident they are all false positives.
                    for e in potential_violation.expected_diffs:
                        def predicate(pv: PotentialViolation):
                            return e in pv.expected_diffs
                        ground_truth = {
                            "partial_order": str(mp),
                            "left_preserve_all": [str(e)]
                        }
                        yield predicate, ground_truth
                case _:
                    raise RuntimeError("Pattern matching on main partial order failed.")

