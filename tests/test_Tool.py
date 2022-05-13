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


from src.ecstatic import Tool
from src.ecstatic import Option
from src.ecstatic import Constraint


def test_constructor():
    t = Tool("FlowDroid")
    assert t.name == "FlowDroid"


def test_add_options():
    t = Tool("")
    t.add_option(Option("aliasalgo"))
    assert Option("aliasalgo") in t.options


def test_add_constraint():
    t = Tool("")
    o1 = Option("cgalgo")
    o1.add_level("CHA")
    o1.add_level("RTA")
    o2 = Option("enablereflection")
    o2.add_level("TRUE")
    o2.add_level("FALSE")
    t.add_option(o1)
    t.add_option(o2)
    c = Constraint(o1, "CHA", o2, "TRUE")
    t.add_constraint(c)
    assert o1 in t.options and o2 in t.options and\
        c in t.constraints
