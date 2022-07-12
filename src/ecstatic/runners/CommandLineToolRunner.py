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
import os
import subprocess
from abc import ABC, abstractmethod
from typing import List

from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util.UtilClasses import BenchmarkRecord, FuzzingJob

logger = logging.getLogger(__name__)

"""
This class supports the basics of running a command line tool,
which allows setting input and output via a command line option.
"""


class CommandLineToolRunner(AbstractCommandLineToolRunner, ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_timeout_option(self) -> List[str]:
        """Set the timeout, using the self.timeout property."""
        pass

    @abstractmethod
    def get_base_command(self) -> List[str]:
        pass

    def get_whole_program(self) -> List[str]:
        """If supported, this should return an option to enable whole-program analysis.
        Necessary for Dacapo benchmarks."""
        pass

    @abstractmethod
    def get_input_option(self, benchmark_record: BenchmarkRecord) -> List[str]:
        """Returns option that should prepend the input program."""
        pass

    @abstractmethod
    def get_output_option(self, output_file: str) -> List[str]:
        """Returns option that should prepend the output."""
        pass

    def get_task_option(self, task: str) -> List[str]:
        """Given a task, sets the appropriate option.
        Currently not implemented, because every tool only has one task.
        If we allow multiple tasks for each tool, then we will have to include this."""
        pass

    @abstractmethod
    def get_timeout_option(self) -> List[str]:
        """Add an option to handle timeout, using self.timeout"""
        pass

    def try_run_job(self, job: FuzzingJob, output_folder: str) -> str:
        """
        Tries to run the job. Judges if a job exists by checking if the expected output file exists. Throws an exception
        if the expected output does not exist.
        Parameters
        ----------
        job: The job to run.
        output_folder: The output folder.

        Returns
        -------
        The location of the result, or throws an exception if running the job failed.
        """
        logging.info(f'Job configuration is {[(str(k), str(v)) for k, v in job.configuration.items()]}')
        config_as_str = self.dict_to_config_str(job.configuration)
        cmd = self.get_base_command()
        cmd.extend(config_as_str.split(" "))
        output_file = self.get_output(output_folder, job)
        output = self.run_from_cmd(cmd, job, output_file)
        if not os.path.exists(output_file):
            raise RuntimeError(output)
        return output_file

    def run_from_cmd(self, cmd: List[str], job: FuzzingJob, output_file: str) -> str:
        """
        Tries to run the cmd specified in cmd. Returns the output, combined from stdout and stderr.
        Parameters
        ----------
        cmd: The command to run.
        job: The job we are running.
        output_file: The output file.

        Returns
        -------
        The combined stdout and stderr of running the command.
        """
        cmd.extend(self.get_input_option(job.target))
        cmd.extend(self.get_output_option(output_file))
        if self.timeout is not None:
            cmd.extend(self.get_timeout_option())
        if self.whole_program:
            cmd.extend(self.get_whole_program())
        cmd = [c for c in cmd if c != '']
        logging.info(f"Cmd is {' '.join(cmd)}")
        ps = subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
        logging.debug(ps.stdout)
        return ps.stdout
