import hashlib
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.util.UtilClasses import FinishedFuzzingJob, FuzzingJob

logger = logging.getLogger("AbstractCommandLineToolRunner")
"""
Base class for command line tool runners.
"""


class AbstractCommandLineToolRunner(ABC):

    def __init__(self, output: str):
        self.output = output

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

    def run_job(self, job: FuzzingJob) -> FinishedFuzzingJob | None:
        num_runs = 0
        while num_runs < 3 and not os.path.exists(
                self.get_output(job) + '.error'):  # TODO: Have this number configurable.
            # noinspection PyBroadException
            try:
                return self.try_run_job(job)
            except Exception:
                num_runs += 1
                logger.exception(f"Failed running job {num_runs} time(s). Trying again...")

        # If we get here we failed too many times and we just abort.
        logger.critical("Failed running job maximum number of times. Sorry!")
        # Create a file so we know not to retry this job in the future.
        with open(self.get_output(job) + '.error', 'w'):
            pass
        return None

    def get_output(self, job: FuzzingJob):
        return os.path.join(self.output,
                            f'{self.dict_hash(job.configuration)}_{os.path.basename(job.target.name)}.raw')

    @abstractmethod
    def try_run_job(self, job: FuzzingJob) -> FinishedFuzzingJob:
        pass

    @staticmethod
    def dict_hash(dictionary: Dict[Option, Level]) -> str:
        """MD5 hash of a dictionary.
        Coopied from https://www.doc.ic.ac.uk/~nuric/coding/how-to-hash-a-dictionary-in-python.html
        """
        dhash = hashlib.md5()
        clone = {str(k): str(v) for k, v in dictionary.items()}
        # We need to sort arguments so {'a': 1, 'b': 2} is
        # the same as {'b': 2, 'a': 1}
        encoded = json.dumps(clone, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()
