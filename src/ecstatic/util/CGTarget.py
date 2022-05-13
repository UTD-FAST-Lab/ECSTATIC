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


from dataclasses import dataclass


@dataclass(eq=False, unsafe_hash=False)
class CGTarget:
    target: str
    context: str

    def __hash__(self):
        return hash(self.target)

    def __eq__(self, other):
        return isinstance(other, CGTarget) and self.target == other.target

    def as_dict(self):
        return {'target': self.target,
                'context': self.context}

    def __lt__(self, other):
        return self.target < other.target
