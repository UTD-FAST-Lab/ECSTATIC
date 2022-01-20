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


import logging
from typing import List

from checkmate.models.Level import Level


def convert_to_int(i: str):
    """
    Converts string to int if possible.
    param i: the string to try to convert.
    :return: the int representation if possible, otherwise the string.
    """
    if i.isdigit():
        return int(i)
    if i[0] == '-' and i[1:].isdigit():
        return int(i)
    else:
        return i


def compare_helper(level, o1: Level, o2: Level):
    # If both are the same, don't compare them
    if (o1, o2) in level:
        # o1 is more precise/sound as o2
        return 1
    if (o2, o1) in level:
        return -1

    return 0


def add_partial_order(level, o1: Level, o2: Level):
    """Helper function to add to any of the partial order lists"""
    if (o1, o2) not in level:
        level.append((o1, o2))


def get_index(level, o):
    """
    recursively find the index of level in o

    l could be:
    1. a list with nested sets
    2. a set
    3. a level, either an int or string.
    """
    # if we've matched, return 0 (treat o as the first
    #  element in the singleton list l
    print(f'Getting index of {o} in {level}')
    if level == o:
        logging.info(f'__get_index: returning 0 for arguments {level} and {o}')
        return 0
    else:
        for i, r in enumerate(level):
            if str(o) in r:
                logging.info(f'__get_index: returning {i} for arguments {level} and {o}')
                return i

    logging.info(f'__get_index: returning -1 for arguments {level} and {o}')
    return -1


def more_precise_or_sound_levels(list_of_levels: List[tuple[Level, Level]], level):
    """Returns the more precise/sound levels of a level.
    (depending on the value of list_of_levels)"""
    ix = get_index(list_of_levels, level)
    if ix < 0:
        raise ValueError(f"{level} is not in {list_of_levels}")
    else:
        try:
            return list_of_levels[ix + 1:]
        except IndexError:
            return []


class Option:
    """ A single configuration option. """
    soundness = 0
    precision = 0

    def __init__(self, name):
        self.name = name
        self.precision = list()
        self.soundness = list()
        self.all = set()
        self.constraints = list()
        self.tags = set()
        self.default = None
        self.options_involved_in_partial_orders = set()

    def set_default(self, default: str):
        """Set default value."""
        self.default = self.get_level(default)

    def get_default(self) -> Level:
        """Return default setting."""
        return self.default

    def add_tag(self, t):
        """Adds a tag."""
        self.tags.add(t)

    def get_tags(self):
        """Returns tags"""
        return self.tags

    def add_constraint(self, o1, o2):
        """Add a disability constraint between two levels."""

    def add_level(self, level):
        """Add a level of the option to the master list."""
        self.all.add(Level(self.name, level))

    def get_levels(self):
        """Returns list of all registered levels"""
        return self.all

    def get_level(self, name: str) -> Level:
        for l in self.all:
            l: Level
            if l.level_name == name:
                return l
        raise ValueError(f'Level {name} has not been added to option {self.name}.')

    def set_more_precise_than(self, o1, o2):
        """
        Add a precision relationship, that o1 is more precise than
        o2. Either o1 or o2 can be a level, a list of levels, or a
        "*", indicating all.
        """
        Option.precision += 1
        Option.soundness += 2
        o1 = self.get_level(o1)
        o2 = self.get_level(o2)
        self.options_involved_in_partial_orders.add(o1)
        self.options_involved_in_partial_orders.add(o2)
        add_partial_order(self.precision, o1, o2)
        add_partial_order(self.soundness, o1, o2)
        add_partial_order(self.soundness, o2, o1)
        logging.debug(f'{self.name} Soundness constraint: {self.soundness}')
        logging.debug(f'{self.name} Precision constraint: {self.precision}')

    def set_more_sound_than(self, o1, o2):
        """
        Add a soundness relationship, that o1 is at least as sound as 
        o2.
        """
        Option.soundness += 1
        o1 = self.get_level(o1)
        o2 = self.get_level(o2)
        self.options_involved_in_partial_orders.add(o1)
        self.options_involved_in_partial_orders.add(o2)
        add_partial_order(self.soundness, o1, o2)
        logging.debug(f'{self.name} Soundness constraint: {self.soundness}')

    def is_more_sound(self, o1: Level, o2: Level) -> bool:
        return (o1, o2) in self.soundness

    def is_more_precise(self, o1: Level, o2: Level) -> bool:
        return (o1, o2) in self.precision

    def precision_compare(self, o1: Level, o2: Level):
        """
        Returns 0 if o1 and o2 are at the same level in terms of precision,
        -1 if o2 is at least as precise as o1, and
        1 is o1 is at least as precise as o2.
        """
        return compare_helper(self.precision, o1, o2)

    def soundness_compare(self, o1: Level, o2: Level):
        return compare_helper(self.soundness, o1, o2)

    def __eq__(self, other):
        return isinstance(other, Option) and \
               self.all == other.all and \
               self.precision == other.precision and \
               self.soundness == other.soundness and \
               self.name == other.name and \
               self.tags == other.tags

    def __hash__(self):
        return hash((frozenset(self.all),
                     tuple([frozenset(p) if isinstance(p, set)
                            else p for p in self.precision]),
                     tuple([frozenset(s) if isinstance(s, set)
                            else s for s in self.soundness]),
                     self.name,
                     frozenset(self.tags)))

    def __str__(self):
        return self.name

    def __lt__(self, other):
        if not isinstance(other, Option):
            raise TypeError('Can only compare options to options.')
        return self.name < other.name

    def as_dict(self):
        return {'name': self.name,
                'precision': self.precision,
                'soundness': self.soundness,
                'all': frozenset(self.all),
                'tags': self.tags}

    def more_precise_than(self, level):
        """Returns levels that are more precise than this level"""
        return more_precise_or_sound_levels(self.precision, level)

    def more_sound_than(self, level):
        """Returns levels that re more sound than this level"""
        return more_precise_or_sound_levels(self.soundness, level)

    @staticmethod
    def from_dict(d):
        o = Option(d['name'])
        o.all = d['all']
        o.precision = d['precision']
        o.soundness = d['soundness']
        o.tags = d['tags']
        return o
