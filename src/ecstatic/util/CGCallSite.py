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


@dataclass
class CGCallSite():
    clazz: str
    stmt: str
    context: str

    def __hash__(self):
        return hash((self.clazz, self.stmt))

    def __eq__(self, other):
        return isinstance(other, CGCallSite) and self.clazz == other.clazz and self.stmt == other.stmt

    def __lt__(self, other):
        if self.clazz != other.clazz:
            return self.clazz < other.clazz
        else:
            return self.stmt < other.stmt

