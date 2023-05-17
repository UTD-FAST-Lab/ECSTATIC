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

import logging
from typing import List, Tuple

from src.ecstatic.readers.AbstractReader import AbstractReader


logger = logging.getLogger(__name__)
class AmanDroidReader(AbstractReader):

    def import_file(self, file):
        flows: List[Tuple[str, str]] = []
        isFlow = False
        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                if isFlow:
                    if 'Source:' in line:
                        source = line.split(': ', 1)[1]
                    elif 'Sink:' in line:
                        sink = line.split(': ', 1)[1]
                        flows.append((source, sink))
                        isFlow = isFlow == False
                else:
                    if 'TaintPath:' in line:
                        isFlow = isFlow == False
        return flows
    