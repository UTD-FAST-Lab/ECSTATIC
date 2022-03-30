from typing import List

from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner


class SOOTRunner(CommandLineToolRunner):
    def get_input_option(self) -> str:
        return "--process-dir"

    def get_output_option(self) -> str:
        return "--callgraph-output"

    def get_task_option(self, task: str) -> str:
        if task == 'cg':
            return "-p cg.spark enabled:true"
        else:
            raise NotImplementedError(f'SOOT does not support task {task}.')

    def get_base_command(self) -> List[str]:
        return "java -jar /SootInterface/target/SootInterface-1.0-SNAPSHOT-jar-with-dependencies.jar -pp -w".split(" ")