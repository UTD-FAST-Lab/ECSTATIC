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

from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.runners.DOOPRunner import DOOPRunner
from src.ecstatic.runners.FlowDroidRunner import FlowDroidRunner
from src.ecstatic.runners.SOOTRunner import SOOTRunner
from src.ecstatic.runners.WALAJSRunner import WALAJSRunner
from src.ecstatic.runners.WALARunner import WALARunner
from src.ecstatic.runners.TAJSRunner import TAJSRunner

logger = logging.getLogger(__name__)


def get_runner_for_tool(name: str, *args) -> AbstractCommandLineToolRunner:
    match name.lower():
        case "soot": return SOOTRunner(*args)
        case "wala": return WALARunner(*args)
        case "doop": return DOOPRunner(*args)
        case "flowdroid": return FlowDroidRunner(*args)
        case "wala-js": return WALAJSRunner(*args)
        case "tajs": return TAJSRunner(*args)
        case _ : raise NotImplementedError(f"No support for runner for {name}")
