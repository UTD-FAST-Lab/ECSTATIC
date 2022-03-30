import logging
import os
import re
import shutil
import subprocess
import time
from typing import List

from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner
from src.checkmate.util.FuzzingJob import FuzzingJob
from src.checkmate.util.UtilClasses import FinishedFuzzingJob


class DOOPRunner(CommandLineToolRunner):
    def get_input_option(self) -> str:
        return "-i"

    def get_output_option(self) -> str:
        pass

    def get_task_option(self, task: str) -> str:
        if task == 'cg':
            pass
        else:
            raise NotImplementedError(f'DOOP does not support task {task}.')

    def get_base_command(self) -> List[str]:
        return ["doop"]

    def process_line(self, line: str) -> str:
        """DOOP format is  """
        matches = re.match(r"[\[<](.*?)[\]>]\s(.*?)\/(.*?)\s[\[<](.*?)[\]>]\s(.*)", line)
        string = ""
        for i in range(0,5):
            string = f'{string}\t{matches.group(i).strip()}'
        return string.strip()

    def transform(self, output: str) -> str:
        with open(output) as f:
            lines = f.readlines()
        transformed = [self.process_line(l) for l in lines]
        with open(output, 'w') as f:
            f.write("caller\tcallsite\tcalling_context\ttarget\ttarget_context\n")
            f.writelines(transformed)
        return output

    def run_job(self, job: FuzzingJob) -> FinishedFuzzingJob:
        logging.info(f'Job configuration is {[(str(k), str(v)) for k, v in job.configuration.items()]}')
        config_as_str = self.dict_to_config_str(job.configuration)
        cmd = self.get_base_command()
        cmd.extend(config_as_str.split(" "))
        output_file = f'{self.dict_hash(job.configuration)}_{os.path.basename(job.apk)}.result'
        cmd.extend([self.get_input_option(), job.apk])
        start_time: float = time.time()
        logging.info(f"Cmd is {cmd}")
        ps = subprocess.run(cmd, capture_output=True)
        for l in ps.stdout.decode().split("\n"):
            print(l)
            if l.startswith("Making database available"):
                output_dir = l.split(" ")[-1]
                break
        intermediate_file = os.path.join(output_dir, "CallGraphEdge.csv")
        shutil.move(intermediate_file, output_file)
        total_time: float = time.time() - start_time
        self.move_to_output(output_file)
        return FinishedFuzzingJob(
            job=job,
            execution_time=total_time,
            results_location=output_file
        )
