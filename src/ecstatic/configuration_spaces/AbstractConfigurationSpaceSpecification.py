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