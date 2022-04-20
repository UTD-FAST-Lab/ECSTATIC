import re
from typing import Tuple

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget


class WALACallGraphReader(AbstractCallGraphReader):
    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        """
        A WALA line looks like:

        < Primordial, Ljava/lang/Class, toString()Ljava/lang/String; >	java/lang/Class:156	Everywhere	java.lang.Class.getName()Ljava/lang/String;	Everywhere
        < Primordial, Ljava/lang/Class, toString()Ljava/lang/String; >	java/lang/Class:156	Everywhere	java.lang.StringBuilder.append(Ljava/lang/String;)Ljava/lang/StringBuilder;	Everywhere        @param line:
        @return:
        """
        tokens = line.split('\t')
        callsite = CGCallSite(tokens[0], tokens[1], tokens[2])
        target = CGCallSite(tokens[3], tokens[4])
        return callsite, target