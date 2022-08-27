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


###
#
# This file is part of ecstatic.
#
# ecstatic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ecstatic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ecstatic.  If not, see <https://www.gnu.org/licenses/>.
###
import logging
from typing import Tuple, Set, Collection

import networkx
from networkx import DiGraph

from src.ecstatic.models.Level import Level
from src.ecstatic.util.PartialOrder import PartialOrder, PartialOrderType


class Option:
    """ A single configuration option. """
    soundness = 0
    precision = 0

    def __hash__(self) -> int:
        return hash((self.name, frozenset(self.all)))

    def __init__(self, name, type="enum",
                 min_value=-2147483648, max_value=2147483647):
        self.partial_orders = set()
        self.name = name
        self.precision = DiGraph()
        self.soundness = DiGraph()
        self.all = set()
        self.constraints = list()
        self.tags = list()
        self.default = None
        self.type: str = type
        self.min_value: int = min_value
        self.max_value: int = max_value

    def __lt__(self, other):
        return self.name < other.name

    def add_tag(self, tag: str):
        self.tags.append(tag)

    def get_levels_involved_in_partial_orders(self) -> Set[Level]:
        opts = set()
        [opts.add(n) for n in self.precision.nodes]
        [opts.add(n) for n in self.soundness.nodes]
        return opts

    def set_default(self, default: str):
        """Set default value."""
        self.default = self.get_level(default)

    def get_default(self) -> Level:
        """Return default setting."""
        return self.default

    def add_level(self, level):
        """Add a level of the option to the master list."""
        if isinstance(level, Level):
            self.all.add(level)
        else:
            self.all.add(Level(self.name, level))

    def get_levels(self) -> Collection[Level]:
        """Returns list of all registered levels"""
        return self.all

    def get_level(self, name: str) -> Level:
        if self.type.startswith('int') and int(name):
            return Level(self.name, name)
        for l in self.all:
            l: Level
            if l.level_name.lower() == name.lower():
                return l
        raise ValueError(f'Level {name} has not been added to option {self.name}.')

    def set_more_precise_than(self, o1, o2):
        """
        Add a precision relationship, that o1 is more precise than
        o2. Either o1 or o2 can be a level, a list of levels, or a
        "*", indicating all.
        """
        if not isinstance(o1, Level):
            o1 = Level(self.name, o1)
        if not isinstance(o2, Level):
            o2 = Level(self.name, o2)
        self.partial_orders.add(PartialOrder(o1, PartialOrderType.MORE_PRECISE_THAN, o2, self))
        self.precision.add_edge(o1, o2, type="explicit")

        # Implicit soundness partial orders
        self.soundness.add_edge(o1, o2, type="implicit")
        self.soundness.add_edge(o2, o1, type="implicit")

    def set_more_sound_than(self, o1, o2):
        """
        Add a soundness relationship, that o1 is at least as sound as 
        o2.
        """
        if not isinstance(o1, Level):
            o1 = Level(self.name, o1)
        if not isinstance(o2, Level):
            o2 = Level(self.name, o2)
        self.partial_orders.add(PartialOrder(o1, PartialOrderType.MORE_SOUND_THAN, o2, self))
        self.soundness.add_edge(o1, o2, type="explicit")

        # Add the implicit precision order that B should be at least as precise as A.
        self.precision.add_edge(o2, o1, type="implicit")

    def resolve_one_node(self, graph: DiGraph, level: Level):
        if graph.has_node(level):
            return level
        else:
            try:
                int(level.level_name)
                node = Level(self.name, 'i')
                if not graph.has_node(node):
                    raise ValueError(f'{level} is numeric, so partial order graph must contain special value i')
            except ValueError:
                raise ValueError(f'{level} is not in graph.')
        return node

    def resolve_nodes(self, graph: DiGraph, o1: str, o2: str) -> Tuple[Level, Level]:
        if not isinstance(o1, Level):
            o1 = Level(self.name, str(o1))
        if not isinstance(o2, Level):
            o2 = Level(self.name, str(o2))
        node1 = self.resolve_one_node(graph, o1)
        node2 = self.resolve_one_node(graph, o2)
        if node1 == node2 and int(o1.level_name) != int(o2.level_name):
            if int(o1.level_name) < int(o2.level_name):
                node1 = Level(self.name, 'i-1')
            elif int(o2.level_name) < int(o1.level_name):
                node2 = Level(self.name, 'i-1')
        return node1, node2

    def check_partial_order(self, p: PartialOrder) -> bool:
        """
        Parameters
        ----------
        p: The partial order

        Returns
        -------
        True if the partial order is in the configuration space, else False.
        """
        if p.type == PartialOrderType.MORE_PRECISE_THAN:
            return self.is_more_precise(p.left, p.right)
        elif p.type == PartialOrderType.MORE_SOUND_THAN:
            return self.is_more_sound(p.left, p.right)
        else:
            raise RuntimeError(f"Can't handle partial order type {p.type}")

    def is_more_sound(self, o1: Level | str, o2: Level | str, allow_implicit: bool = True) -> bool:
        try:
            (node1, node2) = self.resolve_nodes(self.soundness, o1, o2)
            if node2 in networkx.descendants(self.soundness, node1):
                if allow_implicit:
                    return True
                else:
                    return self.soundness.edges[node1, node2]['type'].lower() != 'implicit'
        except ValueError | KeyError as ve:
            logging.debug(ve)
            return False

    def is_more_precise(self, o1: Level | str, o2: Level | str, allow_implicit: bool = True) -> bool:
        try:
            (node1, node2) = self.resolve_nodes(self.precision, o1, o2)
            if node2 in networkx.descendants(self.precision, node1):
                if allow_implicit:
                    return True
                else:
                    return self.precision.edges[node1, node2]['type'].lower() != 'implicit'
        except ValueError | KeyError as ve:
            logging.debug(ve)
            return False


    # def precision_compare(self, o1: Level, o2: Level):
    #     """
    #     Returns 0 if o1 and o2 are at the same level in terms of precision,
    #     -1 if o2 is at least as precise as o1, and
    #     1 is o1 is at least as precise as o2.
    #     """
    #     return compare_helper(self.precision, o1, o2)
    #
    # def soundness_compare(self, o1: Level, o2: Level):
    #     return compare_helper(self.soundness, o1, o2)
    #
    def __eq__(self, other):
        return isinstance(other, Option) and \
               self.name == other.name and \
               self.all == other.all

    #
    # def __hash__(self):
    #     return hash((frozenset(self.all),
    #                  tuple([frozenset(p) if isinstance(p, set)
    #                         else p for p in self.precision]),
    #                  tuple([frozenset(s) if isinstance(s, set)
    #                         else s for s in self.soundness]),
    #                  self.name,
    #                  frozenset(self.tags)))
    #
    def __str__(self):
        return self.name

    #
    # def as_dict(self):
    #     return {'name': self.name,
    #             'precision': self.precision,
    #             'soundness': self.soundness,
    #             'all': frozenset(self.all),
    #             'tags': self.tags}
    #
    # def more_precise_than(self, level):
    #     """Returns levels that are more precise than this level"""
    #     return more_precise_or_sound_levels(self.precision, level)
    #
    # def more_sound_than(self, level):
    #     """Returns levels that re more sound than this level"""
    #     return more_precise_or_sound_levels(self.soundness, level)

    @staticmethod
    def from_dict(d):
        o = Option(d['name'])
        for level in d['levels']:
            o.add_level(Level(o.name, level))
        if 'type' in d:
            o.type = d['type']
        if 'default' in d:
            o.set_default(d['default'])
        if 'minValue' in d:
            o.min_value = int(d['minValue'])
        if 'maxValue' in d:
            o.max_value = int(d['maxValue'])
        if 'tags' in d:
            [o.add_tag(t) for t in d['tags']]
        for p in d['orders']:
            if p['order'] == 'MST':
                o.set_more_sound_than(p['left'], p['right'])
            elif p['order'] == 'MPT':
                o.set_more_precise_than(p['left'], p['right'])
        return o

