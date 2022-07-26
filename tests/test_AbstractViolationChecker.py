from typing import List

from hypothesis import strategies, given
from hypothesis.strategies import composite

from src.ecstatic.models.Option import Option
from src.ecstatic.util.PartialOrder import PartialOrderType


@composite
def get_option(draw, option_name = strategies.text(), level1_name = strategies.text(),
               level2_name = strategies.text(),
               partial_order_type = strategies.one_of(strategies.just(PartialOrderType.MORE_SOUND_THAN),
                                                 strategies.just(PartialOrderType.MORE_PRECISE_THAN))):
    option: Option = Option(draw(option_name))
    level1 = draw(level1_name)
    level2 = draw(level2_name)
    option.add_level(level1)
    option.add_level(level2)
    match (draw(partial_order_type)):
        case PartialOrderType.MORE_PRECISE_THAN:
            option.set_more_precise_than(level1, level2)
        case PartialOrderType.MORE_SOUND_THAN:
            option.set_more_sound_than(level1, level2)
    return option

@given(strategies.lists(strategies.from_regex(r"(?:[^\t\n]+?\t){4}(?:[^\t\n]+)"), min_size=1))
def test_same_callgraph(callgraph: List[str]):

