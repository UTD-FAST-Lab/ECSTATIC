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

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.checkmate.models.Level import Level


class PartialOrderType(Enum):
    MORE_PRECISE_THAN = 'is more precise than'
    MORE_SOUND_THAN = 'is more sound than'


@dataclass
class PartialOrder:
    left: Level
    type: PartialOrderType
    right: Level
    option: Any
    transitive: bool = field(kw_only=True, default=False)

    def __hash__(self):
        return hash((self.left, self.type, self.right))

    def __str__(self):
        return f'{str(self.left)}_{self.type}_{str(self.right)}'

    def is_transitive(self) -> bool:
        from src.checkmate.models.Option import Option # Resolve circular dependency
        if not isinstance(self.option, Option):
            raise RuntimeError(f'{self.option} is not of type Option')
        if type == PartialOrderType.MORE_PRECISE_THAN:
            return not self.option.precision.has_edge(self.left, self.right)
        else:
            return not self.option.soundness.has_edge(self.left, self.right)

