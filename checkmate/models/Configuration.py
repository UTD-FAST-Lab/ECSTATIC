from typing import Dict, Any
from frozendict import frozendict
import re

class Configuration:

    def __init__(self, option_under_investigation: str,
                 configuration: Dict[str, str],
                 config_file : str,
                 file : str):
        self.option_under_investigation = option_under_investigation
        self.configuration = frozendict(configuration)
        self.config_file = config_file
        self.apk = re.search(r"[\w\.]*.apk", file)[0]


    def __eq__(self, o1: Any):
        return isinstance(o1, Configuration) and\
            self.option_under_investigation == o1.option_under_investigation and\
            self.configuration == o1.configuration and\
            self.config_file == o1.config_file and\
            self.apk == o1.apk

    def __hash__(self):
        return hash((self.option_under_investigation, self.configuration,
                     self.config_file, self.apk))

    
