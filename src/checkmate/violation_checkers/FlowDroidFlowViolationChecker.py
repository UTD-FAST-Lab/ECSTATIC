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

from src.checkmate.models.Flow import Flow
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker

logger = logging.getLogger(__name__)

class FlowDroidFlowViolationChecker(AbstractViolationChecker):

    def is_true_positive(self, groundtruth_record: Flow) -> bool:
        return groundtruth_record.get_classification().lower() == 'true'

    def is_false_positive(self, groundtruth_record: Flow) -> bool:
        return groundtruth_record.get_classification().lower() == 'false'

