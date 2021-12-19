from typing import Dict

class FuzzingPairJob:

    def __init__(self, config1: Dict[str, str], config2: Dict[str, str], soundness_level, option_under_investigation):
        self.config1 = config1
        self.config2 = config2
        self.soundness_level = soundness_level
        self.option_under_investigation = option_under_investigation


