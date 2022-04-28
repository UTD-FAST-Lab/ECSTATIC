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

import os.path
import tempfile
from dataclasses import dataclass
from functools import partial
from multiprocessing import Pool
from typing import Iterable

from src.checkmate.readers import ReaderFactory
from src.checkmate.runners import RunnerFactory
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation
import pickle

from src.checkmate.violation_checkers import ViolationCheckerFactory

@dataclass
class DeltaDebuggingResult:
    result: bool
    output: str

class DeltaDebugger:

    def __init__(self, artifacts_folder: str, tool: str, task: str, groundtruths: str = None):
        self.artifacts_folder = artifacts_folder
        self.tool = tool
        self.task = task
        self.groundtruths = groundtruths

    def delta_debug(self, violation: Violation) -> DeltaDebuggingResult:
        """

        Parameters
        ----------
        violation

        Returns
        -------
        True if the delta debugging failed. False otherwise.
        """
        # First, create artifacts. We need to pickle the violation, as well as creating the script.
        violation_tmp = tempfile.NamedTemporaryFile(delete=False, dir=self.artifacts_folder)
        pickle.dump(violation, open(violation_tmp, 'wb'))

        # Then, create the script.
        script_location = self.create_script(violation_tmp)

        # Then, run the delta debugger
        # TODO: Run delta debugger.

        return DeltaDebuggingResult
    def create_script(self, violation_location: str) -> str:
        """
        Given a violation, creates a script that will execute it and return True if the violation is
        preserved.

        Parameters
        ----------
        violation_location: The violation to try to recreate.

        Returns
        -------
        the location of the script.
        """
        with tempfile.NamedTemporaryFile(mode='w', dir=self.artifacts_folder, delete=False) as f:
            f.write("#!/bin/bash\n")
            cmd = f"deltadebugger --violation {violation_location} --target $1 --tool {self.tool} " \
                  f"--task {self.task}"
            if self.groundtruths is not None:
                cmd = f"{cmd} --groundtruths {self.groundtruths}"
            f.write(cmd + "\n")
            result = f.name
        return result


import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--violation", help="The location of the pickled violation.", required=True)
    parser.add_argument("--target", help="The location of the target program.", required=True)
    parser.add_argument("--tool", help="The tool to use.", required=True)
    parser.add_argument("--task", help="The task.", required=True)
    parser.add_argument("--groundtruths", help="Groundtruths (may be None if we are not using ground truths.")
    args = parser.parse_args()

    with open(args.violation) as f:
        violation: Violation = pickle.load(f)

    violation.job1.job.target.name = os.path.abspath(args.target)
    violation.job2.job.target.name = os.path.abspath(args.target)

    # Create tool runner.
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = RunnerFactory.get_runner_for_tool(args.tool)
        reader = ReaderFactory.get_reader_for_task_and_tool(args.task, args.tool)
        checker = ViolationCheckerFactory.get_violation_checker_for_task(args.task, 2, args.groundtruths, reader)
        partial_function = partial(runner.try_run_job, output_folder=tmpdir)
        with Pool(2) as p:
            finishedJobs: Iterable[FinishedFuzzingJob] = p.map(partial_function, [violation.job1, violation.job2])
        violations: Iterable[Violation] = checker.check_violations(finishedJobs, tmpdir)
        for v in violations:
            # Since we already know the target and the configs are the same, we only have to check the partial order.
            if v.partial_orders == violation.partial_orders:
                # 0 means succeed.
                exit(0)
        # 1 means the violation was not recreated.
        exit(1)

