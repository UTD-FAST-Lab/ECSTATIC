import logging
import os
import shutil
import subprocess
import time
from typing import List

from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner
from src.checkmate.util.UtilClasses import BenchmarkRecord, FuzzingJob

logger = logging.getLogger("DOOPRunner")


class DOOPRunner(CommandLineToolRunner):
    def get_input_option(self, benchmark_record: BenchmarkRecord) -> List[str]:
        return f"-i {benchmark_record.name}".split(" ")

    def get_output_option(self, output_file: str) -> List[str]:
        return []

    def get_task_option(self, task: str) -> str:
        if task == 'cg':
            pass
        else:
            raise NotImplementedError(f'DOOP does not support task {task}.')

    def get_base_command(self) -> List[str]:
        return ["doop"]

    def run_from_cmd(self, cmd: List[str], job: FuzzingJob, output_file: str):
        cmd.extend(self.get_input_option(job.target))
        start_time: float = time.time()
        logger.info(f"Cmd is {cmd}")
        ps = subprocess.run(cmd, capture_output=True)
        for line in ps.stdout.decode().split("\n"):
            if line.startswith("Making database available"):
                output_dir = line.split(" ")[-1]
                logger.info(f"Output directory: {output_dir}")
                break
        try:
            intermediate_file = os.path.join(output_dir, "CallGraphEdge.csv")
        except UnboundLocalError as ule:
            logger.exception(ps.stdout.decode().split("\n"))
        shutil.move(intermediate_file, output_file)
        total_time: float = time.time() - start_time
        return total_time
