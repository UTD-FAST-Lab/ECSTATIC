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

from .Option import Option
from .Constraint import Constraint


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
        t.constraints = [Constraint.from_dict(c) for c in d['options']]

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

    def add_constraint(self, constraint: Constraint):
        self.constraints.add(constraint)

    def add_dominates(self, o1: Option, l1: str, o2: Option):
        """
        Adds a dominates relationship, i.e., a level of c1
        disables every level of c2.
        """
        if l1 not in o1.all:
            raise ValueError(f"{l1} is not in {o1}")
        for l in o2.all:
            self.add_constraint(Constraint(o1, l1, o2, l))

    def add_subsumes(self, o1: Option, o2: Option):
        """
        Adds a subsumes relationship, i.e., every level of c1
        dominates c2
        """
        for l1 in o1.all:
            self.add_dominates(o1, l1, o2)
