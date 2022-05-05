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

from src.checkmate.readers import ReaderFactory
from src.checkmate.runners import RunnerFactory
from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.util.BenchmarkReader import validate
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation
from src.checkmate.violation_checkers import ViolationCheckerFactory
from src.checkmate.violation_checkers.AbstractViolationChecker import get_file_name

logger = logging.getLogger(__name__)

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

    def delta_debug(self, violation: Violation, campaign_directory: str, timeout: Optional[int])\
            -> Optional[DeltaDebuggingResult]:
        """

        Parameters
        ----------
        violation

        Returns
        -------
        True if the delta debugging failed. False otherwise.
        @param violation:
        @param timeout:
        @param campaign_directory:
        """
        # First, create artifacts. We need to pickle the violation, as well as creating the script.
        d = os.path.abspath(os.path.join(campaign_directory, 'deltadebugging',
                         os.path.dirname(get_file_name(violation)), os.path.basename((violation.job1.job.target.name))))
        print(f"Making delta debugging directory {d}")
        if os.path.exists(d):
            logger.critical(f'Delta debugging directory {d} already exists. Not removing. Skipping this violation.')
            return None
        Path(d).mkdir(exist_ok=False, parents=True)

        # Copy benchmarks folder so that we have our own code location.
        shutil.copytree(src="benchmarks", dst=os.path.join(d, "benchmarks"))
        violation.job1.job.target = validate(violation.job1.job.target, d)
        logging.info(f'Moved benchmark, so target is now {violation.job1.job.target}')
        violation.job2.job.target = violation.job1.job.target
        try:
            if len(violation.job1.job.target.sources) == 0:
                logging.critical(f"Cannot delta debug benchmark record {violation.job1.job.target} without sources.")
                return None
        except TypeError:
            logging.exception(violation.job1.job.target)

        # Then, create the script.
        script_location = self.create_script(violation, d, timeout)
        build_script = violation.job1.job.target.build_script
        os.chmod(build_script, 700)
        os.chmod(script_location, 700)

        # Then, run the delta debugger
        cmd : List[str]= "java -jar /SADeltaDebugger/ViolationDeltaDebugger/target/ViolationDeltaDebugger-1.0-SNAPSHOT-jar-with" \
              "-dependencies.jar".split(' ')
        sources = [['--sources', s] for s in violation.job1.job.target.sources]
        [cmd.extend(s) for s in sources]
        cmd.extend(["--target", violation.job1.job.target.name])
        cmd.extend(["--bs", os.path.abspath(build_script)])
        cmd.extend(["--vs", os.path.abspath(script_location)])
        cmd.extend(["--logs", os.path.join(d, "log.txt")])
        cmd.extend(['--hdd', '--class-reduction'])
        cmd.extend(['--timeout', '120'])

        print(f"Running delta debugger with cmd {' '.join(cmd)}")
        ps = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, text=True)
        print("Delta debugging completed.")
        # delta_debugging_directory = os.path.join(results_directory)
        # tarname = os.path.join(delta_debugging_directory, get_file_name(violation)) + '.tar.gz'
        # Path(os.path.dirname(tarname)).mkdir(exist_ok=True, parents=True)
        # with tarfile.open(tarname, 'w:gz') as f:
        #     f.add(violation.job1.job.target.name, os.path.basename(violation.job1.job.target.name))
        #     [f.add(s) for s in violation.job1.job.target.sources]
        #     with open(os.path.join(delta_debugging_directory, get_file_name(violation)), 'w') as f1:
        #         json.dump(violation.as_dict(), f1)
        #     f.add(os.path.join(delta_debugging_directory, get_file_name(violation)),
        #           os.path.basename(os.path.join(delta_debugging_directory, get_file_name(violation))))
        #     f.add(os.path.join(d.name, "log.txt"), "log.txt")
        #     os.remove(os.path.join(delta_debugging_directory, get_file_name(violation)))
        #
        # print(f"Delta debugging result written to {tarname}")

    def create_script(self, violation: Violation, directory: str, timeout: Optional[int]) -> str:
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
        violation_tmp = tempfile.NamedTemporaryFile(delete=False, dir=directory)
        pickle.dump(violation, open(violation_tmp.name, 'wb'))
        violation_tmp.close()

        with tempfile.NamedTemporaryFile(mode='w', dir=directory, delete=False) as f:
            f.write("#!/bin/bash\n")
            cmd = f"deltadebugger --violation {violation_tmp.name} " \
                  f"--target {violation.job1.job.target.name} " \
                  f"--tool {self.tool} " \
                  f"--task {self.task} "
            if timeout is not None:
                cmd += f"--timeout {timeout} "
            if self.groundtruths is not None:
                cmd = f"{cmd} --groundtruths {self.groundtruths}"
            f.write(cmd + "\n")
            result = f.name
            logger.info(f"Wrote cmd {cmd} to delta debugging script.")
        return result


import argparse
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument("--violation", help="The location of the pickled violation.", required=True)
    parser.add_argument("--target", help="The location of the target program.", required=True)
    parser.add_argument("--tool", help="The tool to use.", required=True)
    parser.add_argument("--task", help="The task.", required=True)
    parser.add_argument("--groundtruths", help="Groundtruths (may be None if we are not using ground truths.")
    parser.add_argument("--timeout", help="Timeout in minutes.", type=int, default=None)
    args = parser.parse_args()

    with open(args.violation, 'rb') as f:
        violation: Violation = pickle.load(f)

    logger.info(f'Read violation from {args.violation}')
    violation.job1.job.target.name = os.path.abspath(args.target)
    violation.job2.job.target.name = os.path.abspath(args.target)

    # Create tool runner.
    tmpdir = tempfile.TemporaryDirectory()
    runner : AbstractCommandLineToolRunner = RunnerFactory.get_runner_for_tool(args.tool)
    if args.timeout is not None:
        runner.timeout = args.timeout
    reader = ReaderFactory.get_reader_for_task_and_tool(args.task, args.tool)
    checker = ViolationCheckerFactory.get_violation_checker_for_task(args.task, args.tool,
                                                                     2, args.groundtruths, reader)
    partial_function = partial(runner.run_job, output_folder=tmpdir.name)
    with Pool(2) as p:
        finishedJobs: Iterable[FinishedFuzzingJob] = p.map(partial_function, [violation.job1.job, violation.job2.job])
    violations: Iterable[Violation] = checker.check_violations(finishedJobs, tmpdir.name)
    for v in violations:
        # Since we already know the target and the configs are the same, we only have to check the partial order.
        if v.partial_orders == violation.partial_orders:
            logging.info("Violation was recreated! Exiting with 0.")
            # 0 means succeed.
            exit(0)
    # 1 means the violation was not recreated.
    logging.info("Violation was not recreated. Exiting with 1.")
    exit(1)

