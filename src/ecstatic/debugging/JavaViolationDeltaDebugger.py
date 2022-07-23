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
import os.path
import pickle
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable, Optional, List

from src.ecstatic.debugging.AbstractDeltaDebugger import AbstractDeltaDebugger, DeltaDebuggingPredicate
from src.ecstatic.debugging.JavaDeltaDebugger import JavaDeltaDebugger
from src.ecstatic.readers import ReaderFactory
from src.ecstatic.runners import RunnerFactory
from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util.BenchmarkReader import validate
from src.ecstatic.util.PotentialViolation import PotentialViolation
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob
from src.ecstatic.util.Violation import Violation
from src.ecstatic.violation_checkers import ViolationCheckerFactory
from src.ecstatic.violation_checkers.AbstractViolationChecker import get_file_name

logger = logging.getLogger(__name__)


class JavaViolationDeltaDebugger(JavaDeltaDebugger):
    def make_predicates(self, potential_violation: PotentialViolation) -> Iterable[DeltaDebuggingPredicate]:
        if potential_violation.is_violation:
            def predicate(pv: PotentialViolation):
                return pv.is_violation and pv.partial_orders == potential_violation.partial_orders
            gt = {"sample":"sample"}
            return [(predicate, gt)]
        else:
            return []

