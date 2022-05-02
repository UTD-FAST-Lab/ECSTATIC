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

from dataclasses import dataclass
from enum import Enum

from src.checkmate.models.Level import Level


class PartialOrderType(Enum):
    MORE_PRECISE_THAN = 'is more precise than'
    MORE_SOUND_THAN = 'is more sound than'


@dataclass
class PartialOrder:
    left: Level
    type: PartialOrderType
    right: Level

    def __hash__(self):
        return hash((self.left, self.type, self.right))

    def __str__(self):
        return f'{str(self.left)}_{self.type}_{str(self.right)}'
