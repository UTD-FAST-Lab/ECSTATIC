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
from src.ecstatic.debugging.JavaDeltaDebugger import JavaDeltaDebugger
from src.ecstatic.util.PartialOrder import PartialOrder, PartialOrderType
from src.ecstatic.util.PotentialViolation import PotentialViolation

logger = logging.getLogger(__name__)


class JavaBenchmarkDeltaDebugger(JavaDeltaDebugger):
    def make_predicates(self, potential_violation: PotentialViolation) -> Iterable[Tuple[DeltaDebuggingPredicate, GroundTruth]]:
        """
        Returns the predicates and ground truths for a potential violation. If the potential violation's main
        partial order (i.e., in the case that there are two potential partial order violations, we want the partial
        order that matches the order of the jobs, such that job1 has some relationship to job2)
        :param potential_violation:
        :return:
        """
        if not potential_violation.violated:
            match potential_violation.get_main_partial_order().type:
                case PartialOrderType.MORE_SOUND_THAN:
                    # We
                    def predicate(pv: PotentialViolation):
                        return pv.expected_diffs <= potential_violation.expected_diffs

            for e in potential_violation.expected_diffs:
                def predicate(pv: PotentialViolation):
                    return e in pv.expected_diffs
                logger.info(f"Created predicate to make sure result {e} is preserved.")
                yield predicate
