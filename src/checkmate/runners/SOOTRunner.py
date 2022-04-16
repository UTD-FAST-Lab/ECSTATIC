import os.path
from typing import List, Dict

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner


class SOOTRunner(CommandLineToolRunner):
    def check_for_errors(self, lines: str):
        if "Ouuups... something went wrong! Sorry about that." in lines:
            raise RuntimeError("Failed to run.")

    def get_input_option(self) -> str:
        return "--process-dir"

    def get_output_option(self, benchmark: str, dependencies: List[str]) -> str:
        output_str = f'--callgraph-output {os.path.abspath(benchmark)}'
        if len(dependencies) > 0:
            soot_class_path = f'--soot-class-path {":".join([os.path.abspath(d) for d in dependencies])}'
            output_str = output_str + " " + soot_class_path
        return output_str

    def get_task_option(self, task: str) -> str:
        if task == 'cg':
            return "-p cg.spark enabled:true"
        else:
            raise NotImplementedError(f'SOOT does not support task {task}.')

    def dict_to_config_str(self, config_as_dict: Dict[Option, Level]) -> str:
        """
        We need special handling of SOOT's options, because of phase options.
        @param config_as_dict: The dictionary specifying the configuration.
        @return: The corresponding command-line string.
        """
        config_as_str = ""
        for k, v in config_as_dict.items():
            k: Option
            v: Level
            for t in k.tags:
                if t.startswith('phase'):
                    config_as_str = config_as_str + f"-p {t.split(' ')[1]} {k.name}:{v.level_name} "

        # Compute string for the rest of the options who don't have an associated phase.
        rest_of_config = super().dict_to_config_str({k: v for k, v in config_as_dict.items() if
                                                     len([t for t in k.tags if t.startswith('phase')]) == 0})
        if config_as_str != "":
            return config_as_str + rest_of_config
        else:
            return rest_of_config

    def get_base_command(self) -> List[str]:
        return "java -jar /SootInterface/target/SootInterface-1.0-SNAPSHOT-jar-with-dependencies.jar --keep-line-number -pp -w -p cg.spark on-fly-cg:false,enabled:true".split(" ")
