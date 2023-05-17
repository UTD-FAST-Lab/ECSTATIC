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
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


import importlib
import logging
import os
import shutil
import subprocess
import uuid
from typing import Tuple

from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util import FuzzingJob


logger = logging.getLogger(__name__)


class DroidSafeRunner(AbstractCommandLineToolRunner):

    def try_run_job(self, job: FuzzingJob, output_folder: str) -> Tuple[str, str]:
        target_basedir = os.path.join(os.getenv('DROIDSAFE_SRC_HOME'), 'runs')
        app_name = os.path.basename(job.target.name).replace('.apk', '')
        config_hash = self.dict_hash(job.configuration)
        id = uuid.uuid1().hex
        target_dir = os.path.join(target_basedir, f'{config_hash}_{app_name}_{id}')
            
        droidsafe_shell = importlib.resources.path(f"src.resources.tools.droidsafe", "droidsafe.sh")
        cmd = [droidsafe_shell]
        cmd.append(job.target.name)
        cmd.append(f'{config_hash}_{app_name}_{id}')
        cmd.append(self.dict_to_config_str(job.configuration))
        logger.info(f'Running job with configuration {self.dict_hash(job.configuration)} on apk {job.target.name}')
        ps = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        logger.info(f'Stdout for cmd {" ".join([str(c) for c in cmd])} was {ps.stdout}')
        logger.info(f'Job on configuration {self.dict_hash(job.configuration)} on apk {job.target.name} done.')
        
        output_file = self.get_output(output_folder, job)
        
        try:
            target_dir_gen = os.path.join(target_dir, 'droidsafe-gen')
            intermediate_file = os.path.join(target_dir_gen, "info-flow-results.txt")
        except UnboundLocalError:
            raise RuntimeError(ps.stdout)
        shutil.copyfile(intermediate_file, output_file)
        logger.info(f'Copied {intermediate_file} to {output_file}')
        
        return output_file, ps.stdout
    
