from typing import List

from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner
from src.checkmate.util.UtilClasses import BenchmarkRecord


class WALARunner(CommandLineToolRunner):

    def get_timeout_option(self) -> List[str]:
        return f"--timeout {self.timeout*60*1000}".split("")

    def get_whole_program(self) -> List[str]:
        # WALA does not need a whole-program mode.
        return []

    def get_input_option(self, benchmark_record: BenchmarkRecord) -> List[str]:
        return f"--jars {benchmark_record.name}" \
               f"{(':'+':'.join(benchmark_record.depends_on)) if len(benchmark_record.depends_on) > 0 else ''}".split(" ")

    def get_output_option(self, output_file: str) -> List[str]:
        return f"-o {output_file}".split(" ")

    def get_task_option(self, task: str) -> str:
        if task == 'cg':
            pass
        else:
            raise NotImplementedError(f'WALA does not support task {task}.')

    def get_base_command(self) -> List[str]:
        return "java -jar /WALAInterface/target/WALAInterface-1.0-jar-with-dependencies.jar".split(" ")
