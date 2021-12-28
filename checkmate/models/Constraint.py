###
# Copyright 2020 by Austin Mordahl
#
# This file is part of checkmate.
#
# checkmate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# checkmate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with checkmate.  If not, see <https://www.gnu.org/licenses/>.
###

from checkmate.models.Option import Option
from typing import Dict


class Constraint:
    """Represents a disables constraint o1.l1 --(disables)--> o2.l2"""

    def __init__(self, o1: Option, l1: str,
                 o2: Option, l2: str):
        self.o1 = o1
        self.l1 = l1
        self.o2 = o2
        self.l2 = l2

    def __str__(self):
        return f"{self.o1.name}.{self.l1} disables {self.o2.name}.{self.l2}"

    def as_dict(self):
        return {"option1": self.o1.as_dict(),
                "option2": self.o2.as_dict(),
                "level1": self.l1,
                "level2": self.l2}


def from_dict(d: Dict[str, str]) -> Constraint:
    return Constraint(Option.from_dict(d['option1']),
                      d['level1'],
                      Option.from_dict(d['option2']),
                      d['level2'])
