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
import pytest

from src.ecstatic.fuzzing.generators.FuzzGenerator import FuzzGenerator

@pytest.fixture
def generator():
    return FuzzGenerator()

def test_empty_config(generator):
    assert generator.process_config("") == {}


def test_single_boolean_config(generator):
    assert generator.process_config("--testopt") == {"testopt": "TRUE"}


def test_single_numeric_config(generator):
    assert generator.process_config("--testint 4") == {"testint": "4"}


def test_multiple_boolean_config(generator):
    assert generator.process_config("--a --b") == {"a": "TRUE", "b": "TRUE"}


def test_multiple_enum_config(generator):
    assert generator.process_config("--test1 A --test2 BB") == {"test1": "A", "test2": "BB"}


def test_multiple_mixed_config():
    assert process_config("--test1 1 --test2 --test3 ENUM --test4 --test5") == {"test1": "1",
                                                                                "test2": "TRUE",
                                                                                "test3": "ENUM",
                                                                                "test4": "TRUE",
                                                                                "test5": "TRUE"}
