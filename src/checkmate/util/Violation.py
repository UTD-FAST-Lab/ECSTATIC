from typing import List, Dict, Union

from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.util.UtilClasses import FinishedFuzzingJob


class Violation:

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Violation) and self.violated == o.violated \
               and self.type == o.type and self.job1 == o.job1 \
               and self.job2 == o.job2 and self.differences == o.differences

    def __hash__(self) -> int:
        return hash((self.violated, self.type, self.job1, self.job2, self.differences))

    def as_dict(self) -> Dict[str, Union[str, Dict[str, str], List[str]]]:
        return {'violated': self.violated,
                'type': self.type,
                'job1': {
                    'config': AbstractCommandLineToolRunner.dict_to_config_str(self.job1.job.configuration),
                    'result': self.job1.results_location
                },
                'job2': {
                    'config': AbstractCommandLineToolRunner.dict_to_config_str(self.job2.job.configuration),
                    'result': self.job2.results_location
                },
                'option_under_investigation': self.job1.job.option_under_investigation.name if \
                    self.job1.job.option_under_investigation is not None else self.job2.job.option_under_investigation.name,
                'target': self.job1.job.target,
                'differences': self.differences
                }

    def __init__(self, violated: bool, type: str,
                 job1: FinishedFuzzingJob, job2: FinishedFuzzingJob,
                 differences: List[str]):
        self.violated = violated
        self.type = type
        self.job1 = job1
        self.job2 = job2
        self.differences = differences
