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


from src.ecstatic.configuration_spaces.AbstractConfigurationSpaceSpecification import \
    AbstractConfigurationSpaceSpecification
from src.ecstatic.models.Tool import Tool
from src.ecstatic.models.Option import Option


class DroidsafeConfigurationSpace(AbstractConfigurationSpaceSpecification):

    def make_config_space(self) -> Tool:
        ds = Tool("DroidSafe")

        o = Option('kobjsens')
        ops = ['1', '2', '3', '4', '5', '6', '18']
        for k in ops:
            o.add_level(k)
        for i in range(len(ops) - 1):
            o.set_more_sound_than(ops[i + 1], ops[i])
        ds.add_option(o)

        o = Option('nova')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)

        o1 = Option('nojsa')
        for k in ['TRUE', 'FALSE']:
            o1.add_level(k)
        o1.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o1)

        ds.add_dominates(o1, 'TRUE', o)

        o = Option('noclonestatics')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)

        o = Option('limitcontextforcomplex')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)

        o = Option('ignorenocontextflows')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_sound_than('FALSE', 'TRUE')
        ds.add_option(o)

        o = Option('ignoreexceptionflows')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_sound_than('FALSE', 'TRUE')
        ds.add_option(o)

        o = Option('preciseinfoflow')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_precise_than('TRUE', 'FALSE')
        ds.add_option(o)

        o = Option('analyzestringsunfiltered')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_precise_than('TRUE', 'FALSE')
        ds.add_option(o)

        o = Option('filetransform')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_precise_than('TRUE', 'FALSE')
        ds.add_option(o)

        o = Option('multipassfb')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        #    o.is_as_sound('TRUE', 'FALSE')
        ds.add_option(o)

        o = Option('multipassfb')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_sound_than('TRUE', 'FALSE')
        ds.add_option(o)

        o1 = Option('pta')
        for k in ['DEFAULT', 'PADDLE', 'GEOM']:
            o1.add_level(k)
        ds.add_option(o1)

        o = Option('imprecisestrings')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)
        ds.add_dominates(o1, 'PADDLE', o)
        ds.add_dominates(o1, 'GEOM', o)

        o = Option('noclinitcontext')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)
        ds.add_dominates(o1, 'PADDLE', o)
        ds.add_dominates(o1, 'GEOM', o)

        o = Option('typesforcontext')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)
        ds.add_dominates(o1, 'PADDLE', o)
        ds.add_dominates(o1, 'GEOM', o)

        o = Option('limitcontextforstrings')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)
        ds.add_dominates(o1, 'PADDLE', o)
        ds.add_dominates(o1, 'GEOM', o)

        o = Option('limitcontextforgui')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)
        ds.add_dominates(o1, 'PADDLE', o)
        ds.add_dominates(o1, 'GEOM', o)

        o = Option('apicalldepth')
        ops = ['0', '1', '50', '80', '90', '100', '110', '120', '150', '200', '600', '-1']
        for k in ops:
            o.add_level(k)
        for i in range(len(ops) - 1):
            o.set_more_sound_than(ops[i + 1], ops[i])
        ds.add_option(o)
        ds.add_dominates(o1, 'PADDLE', o)
        ds.add_dominates(o1, 'GEOM', o)

        o = Option('implicitflow')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_sound_than('TRUE', 'FALSE')
        ds.add_option(o)

        o = Option('noarrayindex')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_sound_than('FALSE', 'TRUE')
        ds.add_option(o)

        o = Option('nofallback')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_sound_than('FALSE', 'TRUE')
        ds.add_option(o)

        o = Option('noscalaropts')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)

        o = Option('transfertaintfield')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        ds.add_option(o)

        print(f'DroidSafe has {Option.precision} partial orders '
              f'and {Option.soundness} soundness partial orders.')

        return ds
