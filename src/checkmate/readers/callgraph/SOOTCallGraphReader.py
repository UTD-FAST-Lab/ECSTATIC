from src.checkmate.readers.callgraph.CallGraphReader import CallGraphReader


class SOOTCallGraphReader(CallGraphReader):
    def _AbstractCallGraphReader__transform(self, line: str) -> str:
        return super()._AbstractCallGraphReader__transform(line)