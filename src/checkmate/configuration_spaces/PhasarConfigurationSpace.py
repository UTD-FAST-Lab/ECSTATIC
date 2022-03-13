from src.checkmate.configuration_spaces.AbstractConfigurationSpaceSpecification import \
    AbstractConfigurationSpaceSpecification
from src.checkmate.models.Option import Option
from src.checkmate.models.Tool import Tool


class PhasarConfigurationSpace(AbstractConfigurationSpaceSpecification):
    def make_config_space(self) -> Tool:
        phasar = Tool("phasar")

        """Set the dataflow analysis type"""
        dfa = Option('data-flow-analysis')
        dfa_opts = ['IFDSConstAnalysis',
                    'IFDSLinearConstantAnalysis',
                    'IFDSSolverTest',
                    'IFDSTaintAnalysis',
                    'IFDSTypeAnalysis',
                    'IFDSUninitializedVariables',
                    'IDELinearConstantAnalysis',
                    'IDESolverTest',
                    'IDETaintAnalysis',
                    'IDETypeStateAnalysis',
                    'IntraMonoFullConstantPropagation',
                    'IntraMonoSolverTest',
                    'InterMonoSolverTest',
                    'InterMonoTaintAnalysis',
                    'None']
        [dfa.add_level(d) for d in dfa_opts]
        phasar.add_option(dfa)
        
        """ Set the points-to analysis to be used (CFLSteens, CFLAnders)."""
        pta = Option('pointer-analysis')
        pta.add_level('CFLAnders')
        pta.add_level('CFLSteens')
        pta.set_more_precise_than('CFLAnders', 'CFLSteens')
        phasar.add_option(pta)

        """Set the call-graph algorithm to be used."""
        cga = Option('call-graph-analysis')
        cga_opts = ['CHA', 'RTA', 'DTA', 'VTA', 'OTF']
        [cga.add_level(o) for o in cga_opts]
        cga.add_level('NORESOLVE')
        [cga.set_more_sound_than(o, 'NORESOLVE') for o in cga_opts]
        cga.set_more_precise_than('RTA', 'CHA')
        cga.set_more_precise_than('DTA', 'RTA')
        cga.set_more_precise_than('VTA', 'DTA')
        phasar.add_option(cga)

        """Set the soundiness level to be used."""
        soundiness = Option('soundiness')
        [soundiness.add_level(o) for o in ['Sound', 'Soundy', 'Unsound']]
        soundiness.set_more_sound_than('Sound', 'Soundy')
        soundiness.set_more_sound_than('Soundy', 'Unsound')
        phasar.add_option(soundiness)

        return phasar






