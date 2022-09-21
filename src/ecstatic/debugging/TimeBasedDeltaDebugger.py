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

import argparse
import copy
import logging
import os
import pathlib
import shutil
import subprocess
import tempfile
from abc import abstractmethod
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Optional, Callable, TypeAlias, Set, List

import dill as pickle

from src.ecstatic.readers.AbstractReader import AbstractReader, T
from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util.BenchmarkReader import validate
from src.ecstatic.util.PartialOrder import PartialOrder
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob
from src.ecstatic.violation_checkers.AbstractViolationChecker import AbstractViolationChecker

DeltaDebuggingPredicate: TypeAlias = Callable[[FinishedFuzzingJob], bool]


@dataclass
class GroundTruth:
    partial_order: PartialOrder
    left_preserve: Optional[Set[T]]
    right_preserve: Optional[Set[T]]


@dataclass
class DeltaDebuggingJob:
    predicate: DeltaDebuggingPredicate
    finished_job: FinishedFuzzingJob
    runner: AbstractCommandLineToolRunner
    reader: AbstractReader



logger = logging.getLogger(__name__)

def get_file_name(potential_violation: FinishedFuzzingJob) -> pathlib.Path:
    filename = Path(*[
        f'TIMEDELTADEBUG',
        f'{AbstractCommandLineToolRunner.dict_hash(potential_violation.job.configuration)}',
        f'{os.path.basename(potential_violation.job.target.name)}.json'])
    return filename


class TimeBasedDeltaDebugger():

    def __init__(self, runner: AbstractCommandLineToolRunner, reader: AbstractReader,
                 violation_checker: AbstractViolationChecker, maximum_time_in_seconds: int):
        self.runner = runner
        self.reader = reader
        self.violation_checker = violation_checker
        self.maximum_time_in_seconds = maximum_time_in_seconds

    def get_base_directory(self) -> Path:
        return Path("")

    def delta_debug(self, finished_job: FinishedFuzzingJob, campaign_directory: str, timeout: Optional[int]):
        logger.debug("In delta debug.")

        # Skip any violation for which we don't have sources
        if len(finished_job.job.target.sources) < 1:
            logging.warning(f"Skipping violation on target {finished_job.job.target.name} because it has no sources.")
            return

        finished_job: FinishedFuzzingJob = copy.deepcopy(finished_job)
        # First, create artifacts. We need to pickle the violation, as well as creating the script.
        directory = os.path.abspath(os.path.join(campaign_directory, self.get_base_directory(),
                                                 os.path.dirname(get_file_name(finished_job)),
                                                 os.path.basename(finished_job.job.target.name),
                                                 str(0)))
        print(f"Making delta debugging directory {directory}")
        if os.path.exists(os.path.join(directory, "log.txt")):
            logger.critical(
                f'Delta debugging result {os.path.join(directory, "log.txt")} already exists. Not removing. Skipping this violation.')
            return None
        if os.path.exists(directory):
            logger.info("Ignoring existing result")
            shutil.rmtree(directory, ignore_errors=True)
        Path(directory).mkdir(exist_ok=True, parents=True)

        # Copy benchmarks folder so that we have our own code location.
        shutil.copytree(src="/benchmarks", dst=os.path.join(directory, "benchmarks"))
        finished_job.job.target = validate(finished_job.job.target, directory)
        logger.info(f'Moved benchmark, so target is now {finished_job.job.target}')
        finished_job.job.target = finished_job.job.target
        try:
            pass
            # if len(potential_violation.job1.job.target.sources) == 0:
            #    logger.critical(
            #        f"Cannot delta debug benchmark record {potential_violation.job1.job.target} without sources.")
            #    return None
        except TypeError:
            logger.exception(finished_job.job.target)

        # Then, create the script.
        def predicate(f: FinishedFuzzingJob) -> bool:
            return f.execution_time_in_ms >= self.maximum_time_in_seconds * 1000

        job = DeltaDebuggingJob(predicate=predicate,
                                runner=self.runner,
                                reader=self.reader,
                                finished_job=finished_job)

        script_location = self.create_script(job, directory)
        build_script = finished_job.job.target.build_script
        if build_script is not None:
            os.chmod(build_script, 0o766)
        os.chmod(script_location, 0o766)

        cmd = self.get_delta_debugger_cmd(build_script, directory, finished_job, script_location)

        print(f"Running delta debugger with cmd {' '.join(cmd)}")
        fin = subprocess.run(cmd, capture_output=True, text=True)
        with open(Path(directory) / '.stdout', 'w') as f:
            f.writelines(fin.stdout)
        with open(Path(directory) / '.stderr', 'w') as f:
            f.writelines(fin.stderr)
        print("Delta debugging completed.")

    def get_delta_debugger_cmd(self, build_script, directory, finished_job: FinishedFuzzingJob, script_location):
        # Then, run the delta debugger
        cmd: List[str] = "jsdelta ".split(' ')
        cmd.extend(["--cmd", script_location])
        cmd.extend(["--out", directory + "/os.js"])
        cmd.extend([finished_job.job.target.name])
        return cmd


    def create_script(self, job: DeltaDebuggingJob, directory: str) -> str:
        """

        :param job: The delta debugging job.
        :param directory: Where to put the script.
        :return: The location of the script.
        """
        job_tmp = tempfile.NamedTemporaryFile(delete=False, dir=directory)
        pickle.dump(job, open(job_tmp.name, 'wb'))
        job_tmp.close()

        with tempfile.NamedTemporaryFile(mode='w', dir=directory, delete=False) as f:
            f.write("#!/bin/bash\n")
            cmd = f"deltadebugger {job_tmp.name}"
            f.write(cmd + "\n")
            result = f.name
            logger.info(f"Wrote cmd {cmd} to delta debugging script.")
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("job", help="The location of the pickled job.")
    args = parser.parse_args()

    with open(args.job, 'rb') as f:
        job: DeltaDebuggingJob = pickle.load(f)

    logger.info(f'Read delta debugging job from {args.job}')
    # Create tool runner.
    tmpdir = tempfile.mkdtemp(dir = str(Path(args.job).parent))

    partial_function = partial(job.runner.run_job, output_folder=tmpdir)
    finished_job = partial_function(job.finished_job.job)

    exit(0 if job.predicate(finished_job) else 1)