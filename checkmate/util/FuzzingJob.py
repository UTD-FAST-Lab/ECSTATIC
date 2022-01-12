from typing import Dict

from checkmate.models.Level import Level
from checkmate.models.Option import Option


class FuzzingJob:

    def __init__(self,
                 configuration: Dict[Option, Level],
                 option_under_investigation: Option | None,
                 apk: str):
        self.configuration = configuration
        self.option_under_investigation = option_under_investigation
        self.apk = apk
