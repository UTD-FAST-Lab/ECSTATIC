from typing import Tuple

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget


class WALACallGraphReader(AbstractCallGraphReader):
    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        pass