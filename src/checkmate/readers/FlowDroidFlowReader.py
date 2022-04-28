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
import logging
from typing import Iterable
import xml.etree.ElementTree as ElementTree

from src.checkmate.models.Flow import Flow
from src.checkmate.readers.AbstractReader import AbstractReader

logger = logging.getLogger(__name__)
class FlowDroidFlowReader(AbstractReader):

    def import_file(self, file: str) -> Iterable[Flow]:
        try:
            result = [Flow(f) for f in ElementTree.parse(file).getroot().find('flows').findall('flow')]
            logger.info(f'Found {len(result)} flows in file {file}')
            return result
        except AttributeError:
            return []
