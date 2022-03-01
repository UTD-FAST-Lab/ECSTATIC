from checkmate.configuration_spaces.AbstractConfigurationSpaceSpecification import \
    AbstractConfigurationSpaceSpecification
from checkmate.models.Tool import Tool


class PhasarConfigurationSpace(AbstractConfigurationSpaceSpecification):
    def make_config_space(self) -> Tool:
        phasar = Tool("phasar")

