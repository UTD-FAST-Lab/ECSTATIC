import os.path
from typing import List, Dict

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner
from src.checkmate.util.UtilClasses import BenchmarkRecord


class SOOTRunner(CommandLineToolRunner):
    def get_timeout_option(self) -> List[str]:
        # SOOTInterface expects its timeout in milliseconds.
        if self.timeout is None:
            return []
        else:
            return f"--timeout {self.timeout*60*1000}".split(" ")

    def get_input_option(self, benchmark_record: BenchmarkRecord) -> List[str]:
        output = f"--process-dir {benchmark_record.name}"
        if len(benchmark_record.depends_on) > 0:
            output = output + " " + f"--soot-class-path {':'.join(benchmark_record.depends_on)}"
        return output.split(" ")

    def get_output_option(self, output_file: str) -> List[str]:
        return f'--callgraph-output {os.path.abspath(output_file)}'.split(" ")

    def get_task_option(self, task: str) -> str:
        if task == 'cg':
            return "-p cg.spark enabled:true"
        else:
            raise NotImplementedError(f'SOOT does not support task {task}.')

    def dict_to_config_str(self, config_as_dict: Dict[Option, Level]) -> str:
        """
        We need special handling of SOOT's options, because of phase options.
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
        return "java -jar /SootInterface/target/SootInterface-1.0-SNAPSHOT-jar-with-dependencies.jar --keep-line-number -pp " \
               "-w -p cg.spark on-fly-cg:false,enabled:true".split(" ")
