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
from typing import Tuple

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader

logger = logging.getLogger(__name__)


class SOOTCallGraphReader(AbstractCallGraphReader):
    def process_line(self, line: str) -> Tuple[str, str]:
        """
        Cleans up SOOT's output. First, removes the line number. Second, cleans up lambdas, by removing any indices
        that could change as a result of optimizations.
        Parameters
        ----------
        line

        Returns
        -------

        """
        edge = line.split("\t")[0]
        caller = edge.split("==>")[0]
        target = edge.split("==>")[1]
        return caller, target
