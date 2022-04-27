import logging
import os
import subprocess
import time
from abc import ABC, abstractmethod
from typing import List, Tuple

from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.util.UtilClasses import FinishedFuzzingJob, BenchmarkRecord, FuzzingJob

logger = logging.getLogger("CommandLineToolRunner")

"""
This class supports the basics of running a command line tool,
which allows setting input and output via a command line option.
"""


class CommandLineToolRunner(AbstractCommandLineToolRunner, ABC):

    @abstractmethod
    def get_base_command(self) -> List[str]:
        pass

    @abstractmethod
    def get_input_option(self, benchmark_record: BenchmarkRecord) -> List[str]:
        """Returns option that should prepend the input program."""
        pass

    @abstractmethod
    def get_output_option(self, output_file: str) -> List[str]:
        """Returns option that should prepend the output."""
        pass

    @abstractmethod
    def get_task_option(self, task: str) -> str:
        """Given a task, sets the appropriate option."""
        pass

    def transform(self, output: str):
        """
        If necessary, apply any transformations to the output file.
        @param output: The output file.
        @return:
        """
        pass

    def try_run_job(self, job: FuzzingJob, output_folder: str) -> FinishedFuzzingJob:
        logging.info(f'Job configuration is {[(str(k), str(v)) for k, v in job.configuration.items()]}')
        config_as_str = self.dict_to_config_str(job.configuration)
        cmd = self.get_base_command()
        cmd.extend(config_as_str.split(" "))
        output_file = self.get_output(output_folder, job)
        if not os.path.exists(output_file):
            total_time, output = self.run_from_cmd(cmd, job, output_file)
            if not os.path.exists(output_file):
                raise RuntimeError(output)
            self.transform(output_file)
        else:
            with open(os.path.join(
                    os.path.dirname(output_file),
                    '.' + os.path.basename(output_file) + ".time"), 'r') as f:
                total_time = float(f.read().strip())

            logging.info(f'File {output_file} already exists. Not overwriting.')
        logging.info(f"Finished running job. It took {total_time}s")
        return FinishedFuzzingJob(
            job=job,
            execution_time=total_time,
            results_location=output_file
        )

    def run_from_cmd(self, cmd: List[str], job: FuzzingJob, output_file: str) -> str:
        cmd.extend(self.get_input_option(job.target))
        cmd.extend(self.get_output_option(output_file))
        cmd = [c for c in cmd if c != '']
        logging.info(f"Cmd is {' '.join(cmd)}")
        ps = subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
        logging.debug(ps.stdout)
        return ps.stdout
