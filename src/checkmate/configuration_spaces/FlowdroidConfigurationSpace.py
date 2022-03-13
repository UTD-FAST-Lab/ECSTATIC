from src.checkmate.configuration_spaces.AbstractConfigurationSpaceSpecification import \
    AbstractConfigurationSpaceSpecification
from src.checkmate.models.Constraint import Constraint
from src.checkmate.models.Option import Option
from src.checkmate.models.Tool import Tool


class FlowdroidConfigurationSpace(AbstractConfigurationSpaceSpecification):

    def make_config_space(self) -> Tool:
        fd = Tool("FlowDroid")

        o = Option("aplength")
        ops = ['1', '2', '3', '4', '5', '7', '10', '20']
        for k in ops:
            o.add_level(k)

        if self.transitive:
            for k in ops:
                for k1 in ops:
                    if int(k) < int(k1):
                        o.set_more_precise_than(k1, k)
        else:
            for i in range(len(ops) - 1):
                o.set_more_precise_than(ops[i + 1], ops[i])
        o.set_default('5')
        fd.add_option(o)

        o = Option("cgalgo")
        for k in ['CHA', 'RTA', 'VTA', 'GEOM', 'DEFAULT']:
            o.add_level(k)
        o.set_more_precise_than('RTA', 'CHA')
        o.set_more_precise_than('VTA', 'RTA')
        o.set_default('DEFAULT')
        fd.add_option(o)

        o = Option("nothischainreduction")
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_precise_than('FALSE', 'TRUE')
        o.set_default('FALSE')
        fd.add_option(o)

        o = Option('onesourceatatime')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_precise_than('TRUE', 'FALSE')
        o.set_default('FALSE')
        fd.add_option(o)

        o = Option('dataflowsolver')
        for k in ['DEFAULT', 'FLOWINSENSITIVE']:
            o.add_level(k)
        o.set_more_precise_than('DEFAULT',
                                'FLOWINSENSITIVE')
        o.set_default('DEFAULT')
        fd.add_option(o)

        o1 = Option('aliasflowins')
        for k in ['FALSE', 'TRUE']:
            o1.add_level(k)
        o1.set_more_precise_than('FALSE', 'TRUE')
        o1.set_default('FALSE')
        fd.add_option(o1)

        o = Option('singlejoinpointabstraction')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_default('FALSE')
        o.set_more_sound_than('FALSE', 'TRUE')
        fd.add_option(o)

        o = Option('onecomponentatatime')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_sound_than('FALSE', 'TRUE')
        o.set_default('FALSE')
        fd.add_option(o)

        o1 = Option('staticmode')
        for k in ['DEFAULT',
                  'CONTEXTFLOWINSENSITIVE',
                  'NONE']:
            o1.add_level(k)
        o1.set_more_precise_than('DEFAULT', 'CONTEXTFLOWINSENSITIVE')
        o1.set_more_sound_than('DEFAULT', 'NONE')
        o1.set_more_sound_than('CONTEXTFLOWINSENSITIVE', 'NONE')
        o1.set_default('DEFAULT')
        fd.add_option(o1)

        o = Option('nostatic')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_sound_than('FALSE', 'TRUE')
        o.set_default('FALSE')
        fd.add_option(o)

        fd.add_subsumes(o1, o)

        o = Option('aliasalgo')
        for k in ['NONE', 'LAZY', 'DEFAULT', 'PTSBASED']:
            o.add_level(k)
        o.set_default('DEFAULT')
        fd.add_option(o)

        o = Option('codeelimination')
        for k in ['DEFAULT', 'NONE', 'REMOVECODE']:
            o.add_level(k)
        o.set_more_precise_than('REMOVECODE', 'DEFAULT')
        o.set_more_precise_than('DEFAULT', 'NONE')
        o.set_default('DEFAULT')
        fd.add_option(o)

        o1 = Option('implicit')
        for k in ['DEFAULT', 'ARRAYONLY', 'ALL']:
            o1.add_level(k)
        o1.set_more_sound_than('ARRAYONLY', 'DEFAULT')
        o1.set_default('DEFAULT')
        fd.add_option(o1)
        fd.add_constraint(Constraint(o1, 'ALL', o, 'REMOVECODE'))

        o = Option('nocallbacks')
        for k in ['FALSE', 'TRUE']:
            o.add_level(k)
        o.set_more_sound_than('FALSE', 'TRUE')
        o.set_default('FALSE')
        fd.add_option(o)

        o1 = Option('callbackanalyzer')
        for k in ['DEFAULT', 'FAST']:
            o1.add_level(k)
        o1.set_more_precise_than('DEFAULT', 'FAST')
        o1.set_default('DEFAULT')
        fd.add_option(o1)

        fd.add_dominates(o, 'TRUE', o1)

        o = Option('maxcallbackspercomponent')
        ops = ['1', '50', '80', '90', '100', '110', '120', '150', '600']
        for k in ops:
            o.add_level(k)
        if self.transitive:
            for k in ops:
                for k1 in ops:
                    if int(k) < int(k1):
                        o.set_more_sound_than(k1, k)
        else:
            for i in range(len(ops) - 1):
                o.set_more_sound_than(ops[i + 1], ops[i])
        o.set_default('100')
        fd.add_option(o)

        o = Option('maxcallbacksdepth')
        ops.append('-1')
        for k in ops:
            o.add_level(k)
        if self.transitive:
            for k in ops:
                for k1 in ops:
                    if int(k) != int(k1) and int(k) != -1:
                        o.set_more_sound_than(k, k1)
                    elif int(k) < int(k1):
                        o.set_more_sound_than(k1, k)
        else:
            for i in range(len(ops) - 1):
                o.set_more_sound_than(ops[i + 1], ops[i])
        o.set_default('-1')
        fd.add_option(o)

        o = Option('enablereflection')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_sound_than('TRUE', 'FALSE')
        o.set_default('FALSE')
        fd.add_option(o)

        o = Option('pathalgo')
        for k in ['DEFAULT', 'CONTEXTINSENSITIVE', 'SOURCESONLY']:
            o.add_level(k)
        o.set_more_precise_than('DEFAULT', 'CONTEXTINSENSITIVE')
        o.set_more_precise_than('DEFAULT', 'SOURCESONLY')
        o.set_default('DEFAULT')
        fd.add_option(o)

        o = Option('pathspecificresults')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_precise_than('TRUE', 'FALSE')
        o.set_default('FALSE')
        fd.add_option(o)

        o = Option('noexceptions')
        for k in ['TRUE', 'FALSE']:
            o.add_level(k)
        o.set_more_sound_than('FALSE', 'TRUE')
        o.set_default('FALSE')
        fd.add_option(o)

        o = Option('taintwrapper')
        for k in ['DEFAULT', 'DEFAULTFALLBACK', 'EASY', 'NONE']:
            o.add_level(k)
        o.set_more_sound_than('DEFAULTFALLBACK', 'NONE')
        o.set_more_sound_than('DEFAULTFALLBACK', 'DEFAULT')
        o.set_more_sound_than('EASY', 'NONE')
        o.set_more_sound_than('DEFAULT', 'NONE')
        o.set_default('DEFAULT')
        fd.add_option(o)

        o1 = Option('analyzeframeworks')
        for k in ['TRUE', 'FALSE']:
            o1.add_level(k)
        o1.set_more_sound_than('TRUE', 'FALSE')
        o1.set_default('FALSE')
        fd.add_option(o1)

        fd.add_dominates(o1, 'TRUE', o)

        print(f'FlowDroid has {Option.precision} partial orders '
              f'and {Option.soundness} soundness partial orders.')

        all_options = set()
        for o in fd.get_options():
            o: Option
            for p in [o.precision, o.soundness]:
                for l1, l2 in p:
                    all_options.add((o.name, l1))
                    all_options.add((o.name, l2))

        return fd
