from typing import Dict

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option


class FuzzingJob:

    def __init__(self,
                 configuration: Dict[Option, Level],
                 option_under_investigation: Option | None,
                 apk: str):
        self.configuration = configuration
        self.option_under_investigation = option_under_investigation
        self.target = apk

    def __eq__(self, other):
        return isinstance(other, FuzzingJob) and self.configuration == other.configuration and \
               self.option_under_investigation == other.option_under_investigation and \
               self.target == other.target

    def as_dict(self) -> str:
        return {"option_under_investigation": self.option_under_investigation,
                "configuration": {f"{str(k)}: {str(v)}" for k, v in self.configuration.items()},
                "target": self.target}