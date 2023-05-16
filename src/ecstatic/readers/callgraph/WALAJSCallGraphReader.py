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
from typing import Tuple, Any

from src.ecstatic.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.ecstatic.util.CGCallSite import CGCallSite
from src.ecstatic.util.CGTarget import CGTarget


class WALAJSCallGraphReader(AbstractCallGraphReader):

    def process_line(self, line: str) -> Tuple[Any, Any]:
        match line.split("\t"):
            case [caller_function, caller_line, caller_context, callee_target, callee_context]:
                return CGCallSite(caller_function, caller_line, caller_context), CGTarget(callee_target, callee_context)
            case _: raise ValueError(f"Could not read line {line}")