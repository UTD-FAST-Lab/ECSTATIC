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
from hypothesis import given, strategies, assume

from src.ecstatic.models.Option import Option

@given(strategies.text(min_size=1), strategies.text(min_size=1), strategies.text(min_size=1))
def test_implicit_precision_orders(option_name: str, level1_name: str, level2_name: str):
    """
    Test that adding a soundness partial order adds the appropriate precision partial order.
    :param option_name:
    :param level1_name:
    :param level2_name:
    :return:
    """
    assume(option_name != level1_name and option_name != level2_name and level1_name != level2_name)
    option: Option = Option(option_name)
    option.add_level(level1_name)
    option.add_level(level2_name)
    option.set_more_sound_than(level1_name, level2_name)
    assert (not option.is_more_precise(level1_name, level2_name)) and \
           (option.is_more_precise(level2_name, level1_name)) and \
           (not option.is_more_precise(level2_name, level1_name, allow_implicit=False))

@given(strategies.text(min_size=1), strategies.text(min_size=1), strategies.text(min_size=1))
def test_implicit_soundness_orders(option_name: str, level1_name: str, level2_name: str):
    """
    Tests that adding a precision partial order adds two implicit soundness partial orders.
    :param option_name:
    :param level1_name:
    :param level2_name:
    :return:
    """
    assume(option_name != level1_name and option_name != level2_name and level1_name != level2_name)
    option: Option = Option(option_name)
    option.add_level(level1_name)
    option.add_level(level2_name)
    option.set_more_precise_than(level1_name, level2_name)
    # Check that the implicit soundness partial orders are there but that they are implicit.
    assert option.is_more_sound(level1_name, level2_name) and \
           option.is_more_sound(level2_name, level1_name) and \
           not option.is_more_sound(level1_name, level2_name, allow_implicit=False) and \
           not option.is_more_sound(level2_name, level1_name, allow_implicit=False)