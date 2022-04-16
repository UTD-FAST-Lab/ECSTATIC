import logging
import os
import re
import shutil
import subprocess
import time
from typing import List

from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner
from src.checkmate.util.UtilClasses import FinishedFuzzingJob, BenchmarkRecord, FuzzingJob


class DOOPRunner(CommandLineToolRunner):
    def get_input_option(self, benchmark_record: BenchmarkRecord) -> str:
        return f"-i {benchmark_record.name}"

    def get_output_option(self, output_file: str) -> str:
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

    def run_from_cmd(self, cmd, job, output_file):
        cmd.extend([self.get_input_option(job.target), job.target])
        start_time: float = time.time()
        logging.info(f"Cmd is {cmd}")
        ps = subprocess.run(cmd, capture_output=True)
        for line in ps.stdout.decode().split("\n"):
            if line.startswith("Making database available"):
                output_dir = line.split(" ")[-1]
                logging.info(f"Output directory: {output_dir}")
                break
        try:
            intermediate_file = os.path.join(output_dir, "CallGraphEdge.csv")
        except UnboundLocalError as ule:
            logging.exception(ps.stdout.decode().split("\n"))
        shutil.move(intermediate_file, output_file)
        total_time: float = time.time() - start_time
        return total_time
