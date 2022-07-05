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
from typing import Iterable

from src.ecstatic.debugging.AbstractDeltaDebugger import DeltaDebuggingPredicate
from src.ecstatic.debugging.JavaDeltaDebugger import JavaDeltaDebugger
from src.ecstatic.util.PotentialViolation import PotentialViolation

logger = logging.getLogger(__name__)


class JavaBenchmarkDeltaDebugger(JavaDeltaDebugger):
    def make_predicates(self, potential_violation: PotentialViolation) -> Iterable[DeltaDebuggingPredicate]:
        if not potential_violation.violated:
            for e in potential_violation.expected_diffs:
                def predicate(pv: PotentialViolation):
                    return e in pv.expected_diffs
                logger.info(f"Created predicate to make sure result {e} is preserved.")
                yield predicate
