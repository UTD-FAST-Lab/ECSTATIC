from src.checkmate.runners.CommandLineToolRunner import CommandLineToolRunner


class WALARunner(CommandLineToolRunner):
    def get_input_option(self) -> str:
        pass

    def get_output_option(self) -> str:
        pass

    def get_task_option(self, task: str) -> str:
        if task == 'cg':
            pass
        else:
            raise NotImplementedError(f'WALA does not support task {task}.')

    def get_tool_path(self) -> str:
        pass