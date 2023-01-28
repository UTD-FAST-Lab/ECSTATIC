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
from typing import Iterable, Dict

from src.ecstatic.util.CGCallSite import CGCallSite
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob
from src.ecstatic.violation_checkers.AbstractViolationChecker import AbstractViolationChecker, T

logger = logging.getLogger(__name__)


class CallgraphViolationChecker(AbstractViolationChecker):

    cache: Dict[str, Iterable[T]] = {}

    def postprocess(self, results: Iterable[T], job: FinishedFuzzingJob) -> Iterable[T]:
        orig_length = len(results)
        if len(job.job.target.packages) > 0:
            if isinstance(x[0], CGCallSite):
                results = list(filter(lambda x: True in [x[0].clazz.strip("<>").startswith(p) for p
                                                         in job.job.target.packages], results))
                logging.info(f"Postprocessed result from {orig_length} to {len(results)} edges.")
        return results

    def is_true_positive(self, raw_result: T) -> bool:
        raise NotImplementedError("We do not support classified call graphs yet.")

    def is_false_positive(self, raw_result: T) -> bool:
        raise NotImplementedError("We do not support classified call graphs yet.")
