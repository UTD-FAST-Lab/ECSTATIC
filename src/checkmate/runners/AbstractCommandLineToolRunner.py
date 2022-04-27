import hashlib
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.util.UtilClasses import FinishedFuzzingJob, FuzzingJob, BenchmarkRecord

logger = logging.getLogger("AbstractCommandLineToolRunner")
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

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if isinstance(value, int) and value < 0:
            raise ValueError(f'Timeout must be positive. Supplied number was {value}')
        elif value != None:
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

    def run_job(self, job: FuzzingJob, output_folder: str, num_retries: int = 1) -> FinishedFuzzingJob | None:
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

        exception = None
        num_runs = 0
        while num_runs < num_retries and not os.path.exists(
                self.get_output(output_folder, job) + '.error'):
            # noinspection PyBroadException
            try:
                start = time.time()
                result = self.try_run_job(job, output_folder)
                with open(os.path.join(output_folder,
                                       '.' + os.path.basename(self.get_output(output_folder, job)) + ".time"),
                          'w') as f:
                    f.write(f'{str(time.time() - start)}\n')
                return result
            except Exception as ex:
                exception = ex
                num_runs += 1
                logger.exception(f"Failed running job {num_runs} time(s).")

        # If we get here we failed too many times and we just abort.
        logger.critical("Failed running job maximum number of times. Sorry!")
        # Create a file so we know not to retry this job in the future.
        with open(self.get_output(output_folder, job) + '.error', 'w') as f:
            f.write(str(exception))
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
    def try_run_job(self, job: FuzzingJob, output_folder: str) -> FinishedFuzzingJob:
        """
        Attempt to run the job. Throw an exception if the job fails, otherwise, returns the finished fuzzing job.
        Parameters
        ----------
        job: The job to run.
        output_folder: Where to put outputs. Subclasses may create different directories in this output folder in
        order to store differnt artifacts.

        Returns
        -------
        A finished job if the job was successful, otherwise should throw an exception.
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
