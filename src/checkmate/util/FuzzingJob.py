from typing import Dict, List

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.util.UtilClasses import BenchmarkRecord


class FuzzingJob:

    def __init__(self,
                 configuration: Dict[Option, Level],
                 option_under_investigation: Option | None,
                 target: BenchmarkRecord,
                 target_dependencies: List[str] = []):
        self.configuration = configuration
        self.option_under_investigation = option_under_investigation
        self.target = target

    def __eq__(self, other):
        return isinstance(other, FuzzingJob) and self.configuration == other.configuration and \
               self.option_under_investigation == other.option_under_investigation and \
               self.target == other.target and \
               self.target_dependencies == other.target_dependencies

    def as_dict(self) -> str:
        return {"option_under_investigation": self.option_under_investigation,
                "configuration": {f"{str(k)}: {str(v)}" for k, v in self.configuration.items()},
                "target": self.target,
                "target_dependencies": self.target_dependencies}