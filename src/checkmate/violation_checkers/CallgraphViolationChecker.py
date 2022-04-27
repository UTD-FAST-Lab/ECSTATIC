import logging
from typing import Any, Set, List, Tuple

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker, T

logger = logging.getLogger(__name__)


class CallgraphViolationChecker(AbstractViolationChecker):

    def get_false_positives(self, input: Any) -> Set[T]:
        raise NotImplementedError("We do not support classified call graphs yet.")

    def get_true_positives(self, input: Any) -> Set[T]:
        raise NotImplementedError("We do not support classified call graphs yet.")

    def __init__(self, jobs: int, groundtruths: str, reader: AbstractCallGraphReader):
        self.reader = reader
        super().__init__(jobs, groundtruths)

    def read_from_input(self, file: str) -> List[Tuple[CGCallSite, CGTarget]]:
        logger.info(f'Reading callgraph from {file}')
        callgraph: List[Tuple[CGCallSite, CGTarget]] = self.reader.import_file(file)
        logger.info(f'Finished reading callgraph.')
        return callgraph
