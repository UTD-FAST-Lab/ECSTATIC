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
from src.ecstatic.readers.callgraph.WALAJSCallGraphReader import WALAJSCallGraphReader


def get_reader_for_task_and_tool(task: str, name: str, *args) -> Any:
    match task.lower():
        case "cg":
            match name.lower():
                case "soot": return SOOTCallGraphReader(*args)
                case "wala": return WALACallGraphReader(*args)
                case "wala-js": return WALAJSCallGraphReader(*args)
                case "doop": return DOOPCallGraphReader(*args)
                case _: raise NotImplementedError(f"No support for task {task} on tool {name}")
        case "taint":
            match name.lower():
                case "flowdroid": return FlowDroidFlowReader(*args)
                case _: raise NotImplementedError(f"No support for task {task} on tool {name}")
        case _: raise NotImplementedError(f"No support for task {task}.")
