import os.path
from typing import List, Dict

from src.ecstatic.models.Level import Level
from src.ecstatic.models.Option import Option
from src.ecstatic.runners.CommandLineToolRunner import CommandLineToolRunner
from src.ecstatic.util.UtilClasses import BenchmarkRecord


class TAJSRunner (CommandLineToolRunner):
    def get_timeout_option(self) -> List[str]:
        if self.timeout is None:
            return []
        else:
            return f"-time-limit {self.timeout * 60}".split(" ")

    def get_whole_program(self) -> List[str]:
        # shouldn't be necessary
        return []

    def get_input_option(self, benchmark_record: BenchmarkRecord) -> List[str]:
        return f"{benchmark_record.name}".split()

    def get_output_option(self, output_file: str) -> List[str]:
        # callgraph recieves file path argument
        return f"-callgraph {output_file}".split()
        
    def get_task_option(self, task: str) -> List[str]:
        # might need to add to this
        if task == 'cg':
            return []
        else:
            raise NotImplementedError(f'TAJS does not support task {task}.')

    def dict_to_config_str(self, config_as_dict: Dict[Option, Level]) -> str:
        """
        We need special handling of TAJS's options, because of unsound options and commands without level value


        Parameters
        ----------
        config_as_dict: The dictionary specifying the configuration.
        Returns
        -------
        The corresponding command-line string.
        """
        config_as_str = ""
        for k, v in config_as_dict.items():
            k: Option
            v: Level
            for t in k.tags:
                if t.startswith('unsound'):
                    config_as_str = config_as_str + f"-unsound -{k.name} "
        rest_of_config = ""
        for k, v in config_as_dict.items():
            if len([t for t in k.tags if t.startswith('unsound')]) == 0:
                k: Option
                v: Level
                if isinstance(v.level_name, int) or \
                        v.level_name.lower() not in ['false', 'true']:
                    rest_of_config += f'-{k.name} {v.level_name} '
                elif v.level_name.lower() == 'true':
                    rest_of_config += f'-{k.name} '

        # Compute string for the rest of the options which are not unsound.
        # this part may not work
        return config_as_str + rest_of_config

    def get_base_command(self) -> List[str]:
        return "java -jar dist/tajs-all.jar".split()
        