import logging
from abc import ABC
from typing import Tuple, List, Any

from src.checkmate.readers.AbstractReader import AbstractReader
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget

logger = logging.getLogger(__name__)


class AbstractCallGraphReader(AbstractReader):

    def import_file(self, file: str) -> Any:
        logger.info(f'Reading callgraph from {file}')
        callgraph: List[Tuple[CGCallSite, CGTarget]] = []
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
        callsite = CGCallSite(tokens[0].strip(), tokens[1].strip(), tokens[2].strip())
        target = CGTarget(tokens[3].strip(), tokens[4].strip())
        return callsite, target
