from checkmate.checkmate.models.Tool import Tool
from checkmate.checkmate.models.Option import Option
from checkmate.checkmate.models.Constraint import Constraint


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
