from typing import Any

from src.checkmate.readers.FlowDroidFlowReader import FlowDroidFlowReader
from src.checkmate.readers.callgraph.DOOPCallGraphReader import DOOPCallGraphReader
from src.checkmate.readers.callgraph.SOOTCallGraphReader import SOOTCallGraphReader
from src.checkmate.readers.callgraph.WALACallGraphReader import WALACallGraphReader


def get_reader_for_task_and_tool(task: str, name: str, *args) -> Any:
    if task.lower() == "cg":
        if name.lower() == "soot":
            return SOOTCallGraphReader(*args)
        elif name.lower() == "wala":
            return WALACallGraphReader(*args)
        elif name.lower() == "doop":
            return DOOPCallGraphReader(*args)
        else:
            raise NotImplementedError(f"No support for task {task} on tool {name}")
    elif task.lower() == "taint":
        if name.lower() == "flowdroid":
            return FlowDroidFlowReader(*args)
    raise NotImplementedError(f"No support for task {task}")

