from abc import ABC, abstractmethod
from ..models import Tool


class AbstractConfigurationSpaceSpecification(ABC):

    def __init__(self, transitive: bool = True):
        self.transitive = transitive

    @abstractmethod
    def make_config_space(self) -> Tool:
        pass
