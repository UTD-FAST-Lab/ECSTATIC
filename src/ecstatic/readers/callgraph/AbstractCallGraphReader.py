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
from pathlib import Path
from typing import Tuple, List, Any

from src.ecstatic.readers.AbstractReader import AbstractReader
from src.ecstatic.util.CGCallSite import CGCallSite
from src.ecstatic.util.CGTarget import CGTarget

logger = logging.getLogger(__name__)


class AbstractCallGraphReader(AbstractReader):

    def import_file(self, file: Path) -> Any:
        logger.info(f'Reading callgraph from {file}')
        callgraph: List[Tuple[CGCallSite, CGTarget]] = []
        with open(file) as f:
            lines = f.readlines()
        for line in lines:
            try:
                callgraph.append(self.process_line(line))
            except IndexError:
                logging.critical(f"Could not read line: {line}")
        return list(filter(lambda x: x is not None, callgraph))

    def process_line(self, line: str) -> Tuple[Any, Any]:
        """
        Creates call graph nodes from input line.
        Expects line to have the following format:
        caller\tcallsite\tcalling_context\ttarget\ttarget_context
        """
        tokens = line.split('\t')
        callsite = CGCallSite(tokens[0].strip(), tokens[1].strip(), tokens[2].strip())
        target = CGTarget(tokens[3].strip(), tokens[4].strip())
        return callsite, target
