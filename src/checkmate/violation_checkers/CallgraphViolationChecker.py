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
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker, T

logger = logging.getLogger(__name__)


class CallgraphViolationChecker(AbstractViolationChecker):

    def get_false_positives(self, input: Any) -> Set[T]:
        raise NotImplementedError("We do not support classified call graphs yet.")

    def get_true_positives(self, input: Any) -> Set[T]:
        raise NotImplementedError("We do not support classified call graphs yet.")

    def __init__(self, jobs: int, groundtruths: str, reader: AbstractCallGraphReader):
        self.reader = reader
        super().__init__(jobs, groundtruths)

    def read_from_input(self, file: str) -> List[Tuple[CGCallSite, CGTarget]]:
        logger.info(f'Reading callgraph from {file}')
        callgraph: List[Tuple[CGCallSite, CGTarget]] = self.reader.import_file(file)
        logger.info(f'Finished reading callgraph.')
        return callgraph
