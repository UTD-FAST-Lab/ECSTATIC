#  CheckMate: A Configuration Tester for Static Analysis
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

from src.checkmate.configuration_spaces.AbstractConfigurationSpaceSpecification import \
    AbstractConfigurationSpaceSpecification
from src.checkmate.models.Tool import Tool


class SOOTConfigurationSpace(AbstractConfigurationSpaceSpecification):
    def make_config_space(self) -> Tool:
        soot = Tool('SOOT')

        # TODO: How to model phases and their options?

        """Force transitive resolving of referenced classes."""
        full_resolver = self.make_binary_option('full-resolver')
        full_resolver.set_more_sound_than('TRUE', 'FALSE')
        soot.add_option(full_resolver)

        """Allow unresolved classes"""
        allow_phantom_refs = self.make_binary_option('allow-phantom-refs')
        allow_phantom_refs.set_more_sound_than('FALSE', 'TRUE')
        soot.add_option(allow_phantom_refs)

        """Allow phantom methods and fields in non-phantom classes"""
        allow_phantom_elms = self.make_binary_option('allow-phantom-elms')
        allow_phantom_elms.set_more_sound_than('FALSE', 'TRUE')
        soot.add_option(allow_phantom_elms)

        """Perform intraprocedural optimizations"""
        optimize = self.make_binary_option('optimize')
        optimize.set_more_precise_than('TRUE', 'FALSE')
        soot.add_option(optimize)

        """Perform whole program optimizations"""
        whole_optimize = self.make_binary_option('whole-optimize')
        whole_optimize.set_more_precise_than('TRUE', 'FALSE')
        soot.add_option(whole_optimize)

        """Omit CFG edges to handlers from excepting units which lack side effects"""
        omit_excepting_unit_edges = self.make_binary_option('omit-excepting-unit-edges')
        omit_excepting_unit_edges.set_more_precise_than('TRUE', 'FALSE')
        soot.add_option(omit_excepting_unit_edges)

        """Trim unrealizable exceptional edges from CFGs"""
        trim_cfgs = self.make_binary_option('trim-cfgs')
        trim_cfgs.set_more_precise_than('TRUE', 'FALSE')
        soot.add_option(trim_cfgs)

        return soot