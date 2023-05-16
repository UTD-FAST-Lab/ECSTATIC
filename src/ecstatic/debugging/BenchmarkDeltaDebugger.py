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
from abc import ABC
from pathlib import Path
from typing import Optional

from src.ecstatic.debugging.AbstractDeltaDebugger import AbstractDeltaDebugger
from src.ecstatic.util.PotentialViolation import PotentialViolation


class BenchmarkDeltaDebugger(AbstractDeltaDebugger, ABC):
    def delta_debug(self, pv: PotentialViolation, campaign_directory: str, timeout: Optional[int]):
        super().delta_debug(pv, Path(campaign_directory)/'delta_debugging'/'benchmarks', timeout)