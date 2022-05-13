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


class CGNode:

    def __init__(self, content: str, site: str, context: str):
        self.content = str(content).strip()
        self.site = str(site).strip()
        self.context = str(context).strip()

    def __eq__(self, other):
        return isinstance(other, CGNode) and self.content == other.content and self.context == other.context \
    and self.site == other.site

    def __hash__(self):
        return hash((self.content, self.context))

    def __str__(self):
        return f'Content: {self.content} Context: {self.context}'