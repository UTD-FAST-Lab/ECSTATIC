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
logging.basicConfig(level=logging.DEBUG)


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

    def set_default(self, default: str):
        """Set default value."""
        if default not in self.all:
            raise RuntimeError("Cannot set a default value without first adding it as a level.")
        self.default = default

    def get_default(self) -> str:
        """Return default setting."""
        return self.default
    
    def add_tag(self, t):
        """Adds a tag."""
        self.tags.add(t)

    def get_tags(self):
        """Returns tags"""
        return self.tags
    
    def add_constraint(self, o1, o2):
        """Add a disable constraint between two levels."""
    
    def add_level(self, level):
        """Add a level of the option to the master list."""
        self.all.add(level)

    def get_levels(self):
        """Returns list of all registered levels"""
        return self.all

    def is_as_precise(self, o1, o2):
        """
        Add a precision relationship, that o1 is more precise than
        o2. Either o1 or o2 can be a level, a list of levels, or a
        "*", indicating all.
        """
        Option.precision += 1
        Option.soundness += 2
        Option.__add_partial_order(self, self.precision, o1, o2)
        Option.__add_partial_order(self, self.soundness, o1, o2)
        Option.__add_partial_order(self, self.soundness, o2, o1)
        logging.debug(f'{self.name} Soundness constraint: {self.soundness}')
        logging.debug(f'{self.name} Precision constraint: {self.precision}')

    def is_as_sound(self, o1, o2):
        """
        Add a soundness relationship, that o1 is at least as sound as 
        o2.
        """
        Option.soundness += 1
        Option.__add_partial_order(self, self.soundness, o1, o2)
        logging.debug(f'{self.name} Soundness constraint: {self.soundness}')

    def __get_index(self, l, o, earliest=True):
        """
        recursively find the index of l in o

        l could be:
        1. a list with nested sets
        2. a set
        3. a level, either an int or string.
        """
        # if we've matched, return 0 (treat o as the first
        #  element in the singleton list l
        print(f'Getting index of {o} in {l}')
        if l == o:
            logging.info(f'__get_index: returning 0 for arguments {l} and {o}')
            return 0
        else:
            for i, r in enumerate(l):
                if str(o) in r:
                    logging.info(f'__get_index: returning {i} for arguments {l} and {o}')
                    return i
                
        logging.info(f'__get_index: returning -1 for arguments {l} and {o}')
        return -1
            # # now we need to differentiate between strings, sets, and lists.
            # #  all of them have 'in' defined, so we can't really use
            # #  duck typing
            # if not (isinstance(l, list) or isinstance(l, set)):
            #     # it's not a match as that would have been caught above
            #     return -1
            # else:
            #     # l is a list. l could potentially contain sets (multiple
            #     #  options at the same precision/soundness level.
            #     # in that case, we don't care where in the set the match is.
            #     #  in face, sets aren't even indexable.
            #     # so, we iterate through the list and recursively try to find matches.
            #     #  if it's a match, we put True in the list. Else False. Then,
            #     #  return the first index of True, or -1 if there are no matches.
            #     def is_match(i, o):
            #         # Check if o is a match for list element i, which could be a set or a single element.
            #         if isinstance(i,set):
            #             return Option.__get_index(self, i, o)
            #         else:
            #             return i == o
                
            #     results = [is_match(i, o) for i in l]
            #     print(f'Results for args {l} and {o}: {results}')
            #     for i, r in enumerate(results):
            #         if str(r) not in ['False', '-1']:
            #             return i
            #     return -1

    def __add_partial_order(self, l, o1, o2):
        """Helper function to add to any of the partial order lists"""
        l.append((o1, o2))
 
        # # Inner functions
        # def raise_value_error(v):
        #     """Raise a value error for a value v that is not in self.all"""
        #     raise ValueError(f"{l} is not in the master list. Options "

        #                      "must be registered before they can be "
        #                      "added to a partial order.")

        # def verify_list(self, li):
        #     """
        #     Check if each value in the list is in self.all; 
        #     raise value error if not
        #     """
        #     for l in li:
        #         if l not in self.all:
        #             raise_value_error(l)

        # # '*' means all, so we check those first.
        # if o1 == "*":
        #     if o2 == "*":
        #         raise ValueError("both arguments cannot be '*'")
        #     if isinstance(o2, list):
        #         # Check that every value is registered.
        #         verify_list(o2)
        #     else:
        #         if o2 not in self.all:
        #             raise_value_error(o2)
        #     # if o1 is '*' then that means that everything is more
        #     # precise/sound than o2. so o2 gets put at the front of the list.
        #     l.insert(0, o2)
        # else:
        #     if o2 == "*":
        #         if isinstance(o1, list):
        #             verify_list(o1)
        #         else:
        #             if o1 not in self.all:
        #                 raise_value_error(o1)
        #         # if o2 is '*' then that means that o1 is more
        #         # precise/sound than everything, so o1 gets put at the
        #         # end of the list.
        #         l.append(o1)
        #     else:
        #         # both are lists or values, check that they're in
        #         # the master already
        #         if o2 not in self.all:
        #             if isinstance(o2, list):
        #                 verify_list(o2)
        #             else:
        #                 raise_value_error(o2)
        #         if o1 not in self.all:
                    
        #             if isinstance(o1, list):
        #                 verify_list(o1)
        #             else:
        #                 raise_value_error(o1)
        #         # if they're in the master, o2 needs to be defined in l
        #         # so we know where to put o1
                
        #         try:
        #             # if the list is empty, add o2 as the initial element to it.
        #             if len(l) == 0:
        #                 l.append(o2)
        #                 loc = 0
        #             else:
        #                 loc = Option.__get_index(self, l, o2)

        #             if loc < 0:
        #                 # o2 is not in the list. That means we need to place
        #                 #  o2 relative to o1.
        #                 loc = Option.__get_index(self, l, o1)
        #                 if loc < 0:
        #                     raise ValueError(f"Neither {o1} or {o2} is in {l}.")
        #                 else:
        #                     # o2 needs to go before o1.
        #                     if loc == 0:
        #                         # if o1 is first, we put o2 before it
        #                         l.insert(0, o2)
        #                     else:
        #                         # the element before it becomes a set
        #                         # containing the previous element.
        #                         if isinstance(l[loc-1], set):
        #                             l[loc-1].add(o2)
        #                         else:
        #                             a = set()
        #                             a.add(l[loc-1])
        #                             a.add(o2)
        #                             l[loc-1] = a
                        
        #             if loc < (len(l) - 1):
        #                 # There is something after o2 in the list.
        #                 # that means we need to add the element after o2
        #                 # to a list with o1.
        #                 if isinstance(l[loc + 1], set):
        #                     l[loc+1].add(o1)
        #                 else:
        #                     a = set()
        #                     a.add(l[loc+1])
        #                     a.add(o1)
        #                     l[loc+1] = a
        #             else:
        #                 if l[-1] != o1:
        #                     l.append(o1)
        #         except ValueError as ve:
        #             raise ve

    def __compare_helper(self, l, o1, o2):
        # If both are the same, don't compare them
        o1 = str(o1)
        o2 = str(o2)
        if (o1, o2) in l:
            # o1 is more precise/sound as o2
            return 1
        if (o2, o1) in l:
            return -1

        return 0

        # if isinstance(l, list) or isinstance(l, set):
        #     locs1 = [o1 in le for le in l]
        #     locs2 = [o2 in le for le in l]
        #     loco1 = min(locs1)
        #     loco2 = max(locs2)
        # else:
        #     loco1 = 0 if o1 == l else -1
        #     loco2 = 0 if o2 == l else -1
        
        # logging.debug(f'__compare_helper debug: l is {l}, o1 is {o1} (loc {loco1}), and o2 is {o2} (loc {loco2})')

        # if loco1 < loco2:
        #     return -1
        # if loco1 == loco2:
        #     return 0
        # if loco1 > loco2:
        #     return 1
        
        # if loco1 < 0:
        #     if isinstance(o1, int):
        #         # try wildcard matching:
        #         if loco2 < 0:
        #             # if loco2 is also < 0 then both may need to be
        #             #  wildcard matched. otherwise, only this one
        #             #  may need to be (i.e., match this to k
        #             #  even if it was greater than loco2 because loco2 may
        #             #  be -1, which may have a specific soundness and
        #             #  precision level in some cases.
        #             if o1 == o2:
        #                 # handle equality, both should be k since they're
        #                 # the same number
        #                 o1 = 'k'
        #                 o2 = 'k'
        #             else:
        #                 # band-aid to fix issue where o2 could be default
        #                 if o2 == 'DEFAULT':
        #                     o2 = 5
        #                 o1 = "k" if o1 < o2 else "k+1"
        #                 o2 = "k+1" if o1 == "k" else "k"
        #         else:
        #             o1 = "k"
        #         return Option.__compare_helper(self, l, o1, o2)
        #     else:
        #         # try matching to "*"
        #         if "*" in l:
        #             return Option.__compare_helper(self, l, "*", o2)
        #         else:
        #             raise ValueError(f"{o1} is not in {l}")
        # if loco2 < 0:
        #     # If we got this far, then o1 was matched.
        #     #  So, the only possible scenario is
        #     #  that either o2 is not in the list or
        #     #  o2 needs to be matched to an integer.
        #     #  In this case, it would always be k,
        #     #  since any matching to k + 1 would have
        #     #  been taken care of above.
        #     if isinstance(o2, int):
        #         return Option.__compare_helper(self, l, o1, "k")
        #     elif "*" in l:
        #         return Option.__compare_helper(self, l, o1, "*")
        #     else:
        #         raise ValueError(f"{o2} is not in {l}")
        # if loco1 < loco2:
        #     return -1
        # if loco1 == loco2:
        #     return 0
        # if loco1 > loco2:
        #     return 1

    def __convert_to_int(self, i : str):
        """
        Converts string to int if possible.
        :param i: the string to try to convert.
        :return: the int representation if possible, otherwise the string.
        """
        if i.isdigit():
            return int(i)
        if i[0] == '-' and i[1:].isdigit():
            return int(i)
        else:
            return i

    def precision_compare(self, o1, o2):
        """
        Returns 0 if o1 and o2 are at the same level in terms of precision,
        -1 if o2 is at least as precise as o1, and
        1 is o1 is at least as precise as o2.
        """
        return Option.__compare_helper(self, self.precision, o1, o2)

    def soundness_compare(self, o1, o2):
        return Option.__compare_helper(self, self.soundness, o1, o2)

    def __eq__(self, other):
        return isinstance(other, Option) and\
            self.all == other.all and\
            self.precision == other.precision and\
            self.soundness == other.soundness and\
            self.name == other.name and\
            self.tags == other.tags
    
    def __hash__(self):
        
        return hash((frozenset(self.all),
                     tuple([frozenset(p) if isinstance(p, set)
                            else p for p in self.precision]),
                     tuple([frozenset(s) if isinstance(s, set)
                            else s for s in self.soundness]),
                     self.name,
                     frozenset(self.tags)))

    def as_dict(self):
        return {'name': self.name,
                'precision': self.precision,
                'soundness': self.soundness,
                'all': frozenset(self.all),
                'tags': self.tags}

    def __more_l_levels(self, l, level):
        """Returns the more l levels of a level."""
        ix = Option.__get_index(self, l, level)
        if ix < 0:
            raise ValueError(f"{level} is not in {l}")
        else:
            try:
                return l[ix+1:]
            except IndexError:
                return []

    def more_precise_than(self, level):
        """Returns levels that are more precise than this level"""
        return Option.__more_l_levels(self, self.precision, level)

    def more_sound_than(self, level):
        """Returns levels that re more sound than this level"""
        return Option.__more_l_levels(self, self.soundness, level)
    
    @staticmethod
    def from_dict(self, d):
        o = Option(d['name'])
        o.all = d['all']
        o.precision = d['precision']
        o.soundness = d['soundness']
        o.tags = d['tags']
        return o
