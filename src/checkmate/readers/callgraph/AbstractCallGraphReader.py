import logging
from abc import ABC
from typing import Tuple, Dict, List

from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget

logger = logging.getLogger(__name__)


class AbstractCallGraphReader(ABC):

    def import_graph(self, file: str) -> List[Tuple[CGCallSite, CGTarget]]:
        logger.info(f'Reading callgraph from {file}')
        callgraph: List[Tuple[CGCallSite, CGTarget]] = {}
        with open(file) as f:
            lines = f.readlines()
        for l in lines[1:]:  # skip header line
            callgraph.append(self.process_line(l))
        return callgraph

    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        """
        Creates call graph nodes from input line.
        Expects line to have the following format:
        caller\tcallsite\tcalling_context\ttarget\ttarget_context
        """
        tokens = line.split('\t')
        callsite = CGCallSite(tokens[0], tokens[1], tokens[2])
        target = CGTarget(tokens[3], tokens[4])
        return callsite, target
