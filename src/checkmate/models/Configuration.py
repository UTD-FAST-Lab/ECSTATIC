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

from typing import Dict, Any
from frozendict import frozendict
import re


class Configuration:

    def __init__(self, option_under_investigation: str,
                 configuration: Dict[str, str],
                 config_file: str,
                 file: str):
        self.option_under_investigation = option_under_investigation
        self.configuration = frozendict(configuration)
        self.config_file = config_file
        self.apk = re.search(r'[\w.]*.apk', file)[0]

    def __eq__(self, o1: Any):
        return isinstance(o1, Configuration) and \
               self.option_under_investigation == o1.option_under_investigation and \
               self.configuration == o1.configuration and \
               self.config_file == o1.config_file and \
               self.apk == o1.apk

    def __hash__(self):
        return hash((self.option_under_investigation, self.configuration,
                     self.config_file, self.apk))
