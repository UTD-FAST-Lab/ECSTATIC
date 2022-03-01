from checkmate.configuration_spaces.AbstractConfigurationSpaceSpecification import \
    AbstractConfigurationSpaceSpecification
from checkmate.models.Option import Option
from checkmate.models.Tool import Tool


class DOOPConfigurationSpace(AbstractConfigurationSpaceSpecification):
    def make_config_space(self) -> Tool:
        doop = Tool("DOOP")

        analysis = Option("analysis")
        analysis_levels = ['1-call-site-sensitive',
                           '1-call-site-sensitive+heap',
                           '1-object-1-type-sensitive+heap',
                           '1-object-sensitive',
                           '1-object-sensitive+heap',
                           '1-type-sensitive',
                           '1-type-sensitive+heap',
                           '2-call-site-sensitive+2-heap',
                           '2-call-site-sensitive+heap',
                           '2-object-sensitive+2-heap',
                           '2-object-sensitive+heap',
                           '2-type-object-sensitive+2-heap',
                           '2-type-object-sensitive+heap',
                           '2-type-sensitive+heap',
                           '3-object-sensitive+3-heap',
                           '3-type-sensitive+2-heap',
                           '3-type-sensitive+3-heap',
                           'adaptive-2-object-sensitive+heap',
                           'basic-only',
                           'context-insensitive',
                           'context-insensitive-plus',
                           'context-insensitive-plusplus',
                           'data-flow',
                           'dependency-analysis',
                           'fully-guided-context-sensitive',
                           'micro',
                           'partitioned-2-object-sensitive+heap',
                           'selective-2-object-sensitive+heap',
                           'sound-may-point-to',
                           'sticky-2-object-sensitive']

        [analysis.add_level(l) for l in analysis_levels]
        analysis.set_more_precise_than('1-call-site-sensitive+heap', '1-call-site-sensitive')
        analysis.set_more_precise_than('1-object-1-type-sensitive+heap', '1-object-sensitive+heap')
        analysis.set_more_precise_than('1-object-1-type-sensitive+heap', '1-type-sensitive+heap')
        analysis.set_more_precise_than('1-object-sensitive+heap', '1-object-sensitive')
        analysis.set_more_precise_than('1-type-sensitive+heap', '1-type-sensitive')
        analysis.set_more_precise_than('1-object-sensitive+heap', '1-type-sensitive+heap')
        analysis.set_more_precise_than('1-object-sensitive', '1-type-sensitive')
        analysis.set_more_precise_than('2-call-site-sensitive+2-heap', '2-call-site-sensitive+heap')
        analysis.set_more_precise_than('2-call-site-sensitive+heap', '1-call-site-sensitive+heap')
        analysis.set_more_precise_than('2-object-sensitive+heap', '1-object-1-type-sensitive+heap')
        analysis.set_more_precise_than('2-object-sensitive+2-heap', '2-object-sensitive+heap')
        analysis.set_more_precise_than('2-object-sensitive+heap', '2-type-sensitive+heap')
        analysis.set_more_precise_than('3-object-sensitive+3-heap', '2-object-sensitive+2-heap')
        analysis.set_more_precise_than('3-object-sensitive+3-heap', '3-type-sensitive+3-heap')
        analysis.set_more_precise_than('1-call-site-sensitive', 'context-insensitive')
        analysis.set_more_precise_than('1-type-sensitive', 'context-insensitive')