from src.checkmate.readers.callgraph.CallGraphReader import CallGraphReader


class WALACallGraphReader(CallGraphReader):
    def _AbstractCallGraphReader__transform(self, line: str) -> str:
        return super()._AbstractCallGraphReader__transform(line)