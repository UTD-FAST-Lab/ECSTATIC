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


from src.ecstatic.models.Level import Level
from src.ecstatic.models.Option import Option


class Tool:
    """
    Abstraction of a tool, e.g., FlowDroid.
    """
    def __init__(self, name):
        """Inits tool name"""
        self.name = name
        self.options = set()
        self.constraints = set()

    @staticmethod
    def from_dict(d):
        """Construct a Tool object from a dictionary produced by self.as_dict()"""
        t = Tool(d["name"])
        t.options = [Option.from_dict(o) for o in d['options']]
        return t
        #t.constraints = [from_dict(c) for c in d['options']]

    def as_dict(self):
        """Return the dictionary representation of this object."""
        return {'name': self.name,
                'options': [o.as_dict() for o in self.options],
                'constraints': [c.as_dict() for c in self.constraints]}
        
    def add_option(self, option: Option):
        """Adds options to the options list."""
        self.options.add(option)

    def get_options(self):
        """Returns options"""
        return self.options

    def get_option(self, name: str):
        """Returns the first option that has the name 'name'"""
        for o in self.options:
            o : Option
            if o.name == name:
                return o

    def add_subsumes(self, o1: Option, o2: Option):
        """
        Adds a subsumes relationship, i.e., every level of c1
        dominates c2
        """
        for l1 in o1.all:
            self.add_dominates(o1, l1, o2)
