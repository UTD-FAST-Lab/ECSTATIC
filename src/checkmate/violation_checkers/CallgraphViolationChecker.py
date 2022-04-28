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

import logging
from typing import Any, Set, List, Tuple

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker, T

logger = logging.getLogger(__name__)


class CallgraphViolationChecker(AbstractViolationChecker):

    def is_true_positive(self, input: T) -> bool:
        raise NotImplementedError("We do not support classified call graphs yet.")

    def is_false_positive(self, input: T) -> bool:
        raise NotImplementedError("We do not support classified call graphs yet.")
