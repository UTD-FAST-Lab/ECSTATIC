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


from typing import Any

from src.ecstatic.readers.FlowDroidFlowReader import FlowDroidFlowReader
from src.ecstatic.readers.callgraph.DOOPCallGraphReader import DOOPCallGraphReader
from src.ecstatic.readers.callgraph.SOOTCallGraphReader import SOOTCallGraphReader
from src.ecstatic.readers.callgraph.WALACallGraphReader import WALACallGraphReader


def get_reader_for_task_and_tool(task: str, name: str, *args) -> Any:
    if task.lower() == "cg":
        if name.lower() == "soot":
            return SOOTCallGraphReader(*args)
        elif name.lower() == "wala":
            return WALACallGraphReader(*args)
        elif name.lower() == "doop":
            return DOOPCallGraphReader(*args)
        else:
            raise NotImplementedError(f"No support for task {task} on tool {name}")
    elif task.lower() == "taint":
        if name.lower() == "flowdroid":
            return FlowDroidFlowReader(*args)
    raise NotImplementedError(f"No support for task {task}")

