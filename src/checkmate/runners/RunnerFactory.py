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

from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.runners.DOOPRunner import DOOPRunner
from src.checkmate.runners.FlowDroidRunner import FlowDroidRunner
from src.checkmate.runners.SOOTRunner import SOOTRunner
from src.checkmate.runners.WALARunner import WALARunner

logger = logging.getLogger(__name__)


def get_runner_for_tool(name: str, *args) -> AbstractCommandLineToolRunner:
    if name.lower() == "soot":
        return SOOTRunner(*args)
    elif name.lower() == "wala":
        return WALARunner(*args)
    elif name.lower() == "doop":
        return DOOPRunner(*args)
    elif name.lower() == "flowdroid":
        return FlowDroidRunner(*args)
        raise NotImplementedError(f"No support for runner for {name}")