import os
from threading import Lock
from typing import Dict
import logging
from checkmate.util import config


class FuzzLogger:
    log_file = os.path.join(config.configuration['output_directory'], 'fuzzlog.txt')

    def __init__(self):
        self.lock = Lock()
        if not os.path.exists(self.log_file):
            f = open(self.log_file, 'w')
            f.close()

    def check_if_has_been_run(self, config_to_check: Dict[str, str], apk: str) -> bool:
        with open(self.log_file, 'r') as f:
            lines = f.readlines()

        return f'{str(config_to_check)},{apk}\n' in lines

    def log_new_config(self, config_to_log: str, apk: str):
        self.lock.acquire()
        with open(self.log_file, 'a') as f:
            f.write(f'{str(config_to_log)},{apk}\n')
        self.lock.release()
