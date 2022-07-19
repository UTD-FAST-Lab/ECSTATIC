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


import hashlib
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from src.ecstatic.models.Level import Level
from src.ecstatic.models.Option import Option
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob, FuzzingJob

logger = logging.getLogger(__name__)
"""
Base class for command line tool runners.
"""


class AbstractCommandLineToolRunner(ABC):
    """
    The base class for command-line based tool runners.
    """

    # Timeout in Minutes

    def __init__(self):
        self._timeout = None
        self.whole_program: bool = False

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if isinstance(value, int) and value < 0:
            raise ValueError(f'Timeout must be positive. Supplied number was {value}')
        elif not isinstance(value, int) and value is not None:
            raise ValueError(f'Timeout must be an integer or None. Supplied object was {value}')
        self._timeout = value

    @staticmethod
    def dict_to_config_str(config_as_dict: Dict[Option, Level]) -> str:
        """Transforms a dictionary to a config string"""
        result = ""
        for k, v in config_as_dict.items():
            k: Option
            v: Level
            if isinstance(v.level_name, int) or \
                    v.level_name.lower() not in ['false', 'true']:
                result += f'--{k.name} {v.level_name} '
            elif v.level_name.lower() == 'true':
                result += f'--{k.name} '
        return result.strip()

    def get_time_file(self, output_folder: str, job: FuzzingJob):
        return os.path.join(output_folder,
                            '.' + os.path.basename(self.get_output(output_folder, job)) + '.time')

    def get_error_file(self, output_folder: str, job):
        return os.path.abspath(self.get_output(output_folder, job) + '.error')

    def run_job(self, job: FuzzingJob, output_folder: str, num_retries: int = 1,
                entrypoint_s=False) -> FinishedFuzzingJob | None:
        """
        Runs the job, producing outputs in output_folder. Can try to rerun the job if the execution fails
        (i.e., if try_run_job throws an exception). If we cannot run the job within num_retries tries,
        this will produce a .error file indicating to future executions that we should not try to rerun.

        Parameters
        ----------
        job: The job to run.
        output_folder: The output folder in which to put results.
        num_retries: How many times the job can be run. Values > 1 allow for multiple attempts. Default is 1.

        Returns
        -------
        A FinishedFuzzingJob if running the job was successful. Otherwise None.
        """

        # Create a configurations folder so we can map hashes to configurations.
        configurations_folder = os.path.join(output_folder, 'configurations')
        Path(configurations_folder).mkdir(exist_ok=True, parents=True)
        configuration_file = os.path.join(configurations_folder,
                                          f'{AbstractCommandLineToolRunner.dict_hash(job.configuration)}.txt')
        if not os.path.exists(configuration_file):
            with open(configuration_file, 'w') as f:
                f.write(self.dict_to_config_str(job.configuration))

        start = 0;
        exception = None
        num_runs = 0

        try:
            if not entrypoint_s:
                if os.path.exists(self.get_output(output_folder, job)):
                    logging.info(f'{self.get_output(output_folder, job)} already exists. Returning that.')
                    with open(self.get_time_file(output_folder, job), 'r') as f:
                        execution_time = float(f.read().strip())

                    return FinishedFuzzingJob(job, execution_time, self.get_output(output_folder, job))
        except Exception:
            logging.exception("Time file was not created, so starting over.")
            os.remove(self.get_output(output_folder, job))

        while num_runs < num_retries:
            # noinspection PyBroadException
            try:
                # have to just remove and overwrite the results each time.
                if entrypoint_s:
                    if os.path.exists(self.get_output(output_folder,job)):
                        os.remove(self.get_output(output_folder, job));
                start = time.time()
                result = self.try_run_job(job, output_folder)
                logging.info(f'Successfully ran job! Result is in {result}')
                total_time = time.time() - start
                with open(self.get_time_file(output_folder, job), 'w') as f:
                    f.write(f'{str(total_time)}\n')
                return FinishedFuzzingJob(job, total_time, result)
            except Exception as ex:
                exception = ex
                num_runs += 1
                logger.exception(f"Failed running job {num_runs} time(s).")

        # If we get here we failed too many times and we just abort.
        if os.path.exists(self.get_error_file(output_folder, job)):
            logger.critical(f"Error file {self.get_error_file(output_folder, job)} already exists, aborting.")
        else:
            logger.critical("Failed running job maximum number of times. Sorry!")
            # Create a file so we know not to retry this job in the future.
            if exception is None:
                raise RuntimeError(f"Job {job} failed, but didn't produce an exception.")
            with open(self.get_output(output_folder, job) + '.error', 'w') as f:
                f.write(str(exception))
            with open(self.get_time_file(output_folder, job).replace('.time', '.error.time'), 'w') as f:
                f.write(f'{str(time.time() - start)}')
        return None

    def get_output(self, output_folder: str, job: FuzzingJob) -> str:
        """
        Returns the name of the output file. If this file exists, then the tool will not try to
        rerun it -- rather, it will just return this file.
        Parameters
        ----------
        output_folder: Where to write results.
        job: The job to run.

        Returns
        -------
        The output file name, including the output folder.
        """
        return os.path.join(output_folder,
                            f'{self.dict_hash(job.configuration)}_{os.path.basename(job.target.name)}.raw')

    @abstractmethod
    def try_run_job(self, job: FuzzingJob, output_folder: str) -> str:
        """
        Attempt to run the job. Throw an exception if the job fails, otherwise, returns the finished fuzzing job.
        Parameters
        ----------
        job: The job to run.
        output_folder: Where to put outputs. Subclasses may create different directories in this output folder in
        order to store differnt artifacts.

        Returns
        -------
        The location of the output file.
        """
        pass

    @staticmethod
    def dict_hash(dictionary: Dict[Option, Level]) -> str:
        """MD5 hash of a dictionary.
        Copied from https://www.doc.ic.ac.uk/~nuric/coding/how-to-hash-a-dictionary-in-python.html
        Used to construct output names, to prevent output names from being unwieldy.
        If the configuration space changes, we can expect the hashes to change. However, with a consistent
        configuration space, we can use the hashes to identify runs that have already been complete.
        """
        dhash = hashlib.md5()
        clone = {str(k): str(v) for k, v in dictionary.items()}
        # We need to sort arguments so {'a': 1, 'b': 2} is
        # the same as {'b': 2, 'a': 1}
        encoded = json.dumps(clone, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()
