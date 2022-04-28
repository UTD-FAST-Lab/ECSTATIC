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
from abc import ABC
from typing import Tuple, List, Any

from src.checkmate.readers.AbstractReader import AbstractReader
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget

logger = logging.getLogger(__name__)


class AbstractCallGraphReader(AbstractReader):

    def import_file(self, file: str) -> Any:
        logger.info(f'Reading callgraph from {file}')
        callgraph: List[Tuple[CGCallSite, CGTarget]] = []
        with open(file) as f:
            lines = f.readlines()
        for l in lines[1:]:  # skip header line
            callgraph.append(self.process_line(l))
        return callgraph

    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        """
        Creates call graph nodes from input line.
        Expects line to have the following format:
        caller\tcallsite\tcalling_context\ttarget\ttarget_context
        """
        tokens = line.split('\t')
        callsite = CGCallSite(tokens[0].strip(), tokens[1].strip(), tokens[2].strip())
        target = CGTarget(tokens[3].strip(), tokens[4].strip())
        return callsite, target
