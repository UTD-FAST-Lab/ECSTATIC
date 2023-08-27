#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public Licese for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


import importlib
import logging
import os
import shutil
import subprocess
import uuid
from typing import Tuple, List

from src.ecstatic.runners.CommandLineToolRunner import CommandLineToolRunner
from src.ecstatic.util.UtilClasses import BenchmarkRecord
from src.ecstatic.util import FuzzingJob


logger = logging.getLogger(__name__)

class AmanDroidRunner (CommandLineToolRunner):
    
    def get_timeout_option(self) -> List[str]:
        print("Amandroid does not support the timeout option. Sorry!")
        exit(-1)
        return []

    def get_input_option(self, benchmark_record: BenchmarkRecord) -> List[str]:
        return f"{benchmark_record.name}".split()

    def get_output_option(self, output_file: str) -> List[str]:
        return f"-o {output_file}".split()
    
    def get_base_command(self) -> List[str]:
        return "java -jar /amandroid/argus-saf-3.2.1-SNAPSHOT-assembly.jar t".split()
    
    def try_run_job(self, job: FuzzingJob, output_folder: str) -> Tuple[str, str]:
        logging.info(f'Job configuration is {[(str(k), str(v)) for k, v in job.configuration.items()]}')
        config_hash = self.dict_hash(job.configuration)
        id = uuid.uuid1().hex
        result_dir = f'/amandroid/{config_hash}_{id}/'
        cmd = self.get_base_command()
        cmd.extend(self.get_output_option(result_dir))
        cmd.extend(self.get_input_option(job.target))
        logging.info(f"Cmd is {cmd}")
        print(f"Cmd is {cmd}")

        ps = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        logger.info(f"Stdout from command {' '.join(cmd)} is {ps.stdout}")
        
        try:
            result_dir_full = os.path.join(result_dir, os.path.basename(job.target.name).replace('.apk', ''))
            intermediate_file = os.path.join(result_dir_full, 'result/AppData.txt')
        except UnboundLocalError:
            raise RuntimeError(ps.stdout)
        
        output_file = self.get_output(output_folder, job)
        shutil.move(intermediate_file, output_file)
        logging.info(f'Moved {intermediate_file} to {output_file}')

        if not os.path.exists(output_file):
            raise RuntimeError(ps.stdout)
        return output_file, ps.stdout
    
    
