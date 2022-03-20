from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader


class WALACallGraphReader(AbstractCallGraphReader):
    def _AbstractCallGraphReader__transform(self, line: str) -> str:
        return super()._AbstractCallGraphReader__transform(line)