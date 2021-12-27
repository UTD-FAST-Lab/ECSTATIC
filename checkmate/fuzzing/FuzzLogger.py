import os
from threading import Lock
from typing import Dict

from checkmate.util import config


class FuzzLogger:
    log_file = os.path.join(config.configuration['output_directory'], 'fuzzlog.txt')

    def __init__(self):
        self.lock = Lock()
        if not os.path.exists(self.log_file):
            f = open(self.log_file, 'w')
            f.close()

    def checkIfHasBeenRun(self, config: Dict[str, str], apk: str) -> bool:
        with open(self.log_file, 'r') as f:
            lines = [l.strip().split(',') for l in f.readlines()]

        return [str(config), apk] in lines

    def logNewConfig(self, config: str, apk: str):
        self.lock.acquire()
        with open(self.log_file, 'a') as f:
            f.write(f'{str(config)},{apk}\n')
        self.lock.release()
