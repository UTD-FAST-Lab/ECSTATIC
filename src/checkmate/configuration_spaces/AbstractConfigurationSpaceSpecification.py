from abc import ABC, abstractmethod
from ..models import Tool
from ..models.Option import Option


class AbstractConfigurationSpaceSpecification(ABC):

    def __init__(self, transitive: bool = True):
        self.transitive = transitive

    @abstractmethod
    def make_config_space(self) -> Tool:
        pass

    def make_binary_option(self, name: str, default: str = 'FALSE') -> Option:
        op = Option(name)
        op.add_level('TRUE')
        op.add_level('FALSE')
        op.set_default(default)
        return op