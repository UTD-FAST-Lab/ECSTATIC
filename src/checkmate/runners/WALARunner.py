from typing import List

from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner


class WALARunner(CommandLineToolRunner):
    def get_input_option(self) -> str:
        return "--appJar"

    def get_output_option(self) -> str:
        return "-o"

    def get_task_option(self, task: str) -> str:
        if task == 'cg':
            pass
        else:
            raise NotImplementedError(f'WALA does not support task {task}.')

    def get_base_command(self) -> List[str]:
        return "java -jar /WALAInterface/target/WALAInterface-1.0-jar-with-dependencies.jar".split(" ")
