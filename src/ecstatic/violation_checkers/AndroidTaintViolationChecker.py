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

from src.ecstatic.models.Flow import Flow
from src.ecstatic.violation_checkers.AbstractViolationChecker import AbstractViolationChecker

logger = logging.getLogger(__name__)

class FlowDroidFlowViolationChecker(AbstractViolationChecker):

    def __init__(self, jobs: int, reader: AbstractReader, output_folder: Path, ground_truths: Optional[Path] = None,
                 write_to_files=True):
        self.output_folder = output_folder
        self.jobs: int = jobs
        self.reader = reader
        self.ground_truths: Path = None
        self.write_to_files = write_to_files
        logger.debug(f'Ground truths are {self.ground_truths}')

