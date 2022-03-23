import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.util.FuzzingJob import FuzzingJob
from src.checkmate.util.UtilClasses import FinishedFuzzingJob

"""
Base class for command line tool runners.
"""


class AbstractCommandLineToolRunner(ABC):

    @staticmethod
    def dict_to_config_str(config_as_dict: Dict[Option, Level]) -> str:
        """Transforms a dictionary to a config string"""
        result = ""
        for k, v in config_as_dict.items():
            k: Option
            v: Level
            if v.level_name.lower() not in ['false', 'true', 'default', k.get_default().level_name.lower()]:
                result += f'--{k.name} {v.level_name} '
            elif v.level_name.lower() == 'true':
                result += f'--{k.name} '
        return result

    @abstractmethod
    def run_job(self, job: FuzzingJob) -> FinishedFuzzingJob:
        pass

    @staticmethod
    def dict_hash(dictionary: Dict[str, Any]) -> str:
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