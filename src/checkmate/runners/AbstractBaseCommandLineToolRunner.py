from abc import ABC, abstractmethod
from typing import Dict

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.util.FuzzingJob import FuzzingJob
from src.checkmate.util.UtilClasses import FinishedFuzzingJob

"""
Base class for command line tool runners.
"""


class AbstractBaseCommandLineToolRunner(ABC):

    @staticmethod
    def dict_to_config_str(config_as_dict: Dict[Option, Level]) -> str:
        """Transforms a dictionary to a config string"""
        result = ""
        for k, v in config_as_dict.items():
            k: Option
            v: Level
            if v.level_name.lower() not in ['false', 'true', 'default', k.get_default().lower()]:
                result += f'--{k.name} {v.level_name} '
            elif v.level_name.lower() == 'true':
                result += f'--{k.name} '
        return result

    @abstractmethod
    def run_job(self, job: FuzzingJob) -> FinishedFuzzingJob:
        pass
