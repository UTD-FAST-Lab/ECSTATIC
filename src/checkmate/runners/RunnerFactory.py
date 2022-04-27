import logging

from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.runners.DOOPRunner import DOOPRunner
from src.checkmate.runners.FlowDroidRunner import FlowDroidRunner
from src.checkmate.runners.SOOTRunner import SOOTRunner
from src.checkmate.runners.WALARunner import WALARunner

logger = logging.getLogger(__name__)


def get_runner_for_tool(name: str, *args) -> AbstractCommandLineToolRunner:
    if name.lower() == "soot":
        return SOOTRunner(*args)
    elif name.lower() == "wala":
        return WALARunner(*args)
    elif name.lower() == "doop":
        return DOOPRunner(*args)
    elif name.lower() == "flowdroid":
        return FlowDroidRunner(*args)
        raise NotImplementedError(f"No support for runner for {name}")