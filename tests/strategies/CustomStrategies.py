import random

from hypothesis import strategies

from src.ecstatic.models.Level import Level
from src.ecstatic.models.Option import Option
from src.ecstatic.models.Tool import Tool
from src.ecstatic.util.PartialOrder import PartialOrderType, PartialOrder


@strategies.composite
def level(draw, option: Option, level_name=strategies.text()):
    return Level(option.name, draw(level_name))


@strategies.composite
def partial_order(draw,
                  option,
                  type=strategies.one_of(strategies.just(PartialOrderType.MORE_SOUND_THAN),
                                         strategies.just(PartialOrderType.MORE_PRECISE_THAN))):
    left = draw(level(option))
    right = draw(level(option))
    po_type = draw(type)
    return PartialOrder(left, right, po_type, option)


@strategies.composite
def categorical_option(draw,
                       name=strategies.text(),
                       min_levels=0,
                       max_levels=100,
                       min_level_settings=0,
                       max_level_settings=100):
    levels = draw(strategies.lists(
        strategies.lists(strategies.text(), min_size=min_level_settings, max_size=max_level_settings),
        min_size=min_levels,
        max_size=max_levels))
    option = Option(name)
    for level_list in levels:
        state = draw(strategies.one_of(strategies.just(None),
                                       strategies.just(PartialOrderType.MORE_SOUND_THAN),
                                       strategies.just(PartialOrderType.MORE_PRECISE_THAN)))
        for level in level_list:
            option.add_level(level)
        for ix in range(len(level_list) - 1):
            match state:
                case PartialOrderType.MORE_SOUND_THAN:
                    option.set_more_sound_than(level_list[ix], level_list[ix+1])
                case PartialOrderType.MORE_PRECISE_THAN:
                    option.set_more_precise_than(level_list[ix], level_list[ix+1])
                case None:
                    pass
    return option

@strategies.composite
def option(draw):
    """
    Add more potential draws here if I implement other strategies.
    """
    return draw(categorical_option)

@strategies.composite
def tool(draw, name=strategies.text(),
         options=strategies.lists(option)):
    tool: Tool = Tool(draw(name))
    for o in draw(options):
        tool.add_option(o)
