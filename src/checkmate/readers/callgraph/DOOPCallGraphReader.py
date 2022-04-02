import re

from networkx import DiGraph

from src.checkmate.readers.callgraph.CallGraphReader import CallGraphReader
from src.checkmate.readers.callgraph.CGNode import CGNode


class DOOPCallGraphReader(CallGraphReader):
    def _AbstractCallGraphReader__transform(self, line: str) -> str:
        """DOOP format is  """
        matches = re.match(r"[\[<](.*?)[\]>]\s(.*?)\/(.*?)\s[\[<](.*?)[\]>]\s(.*)", line)
        string = ""
        for i in range(0,5):
            string = f'{string}\t{matches.group(i).strip()}'
        return string.strip()