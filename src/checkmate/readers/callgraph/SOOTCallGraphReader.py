import re
import sre_compile
from typing import Tuple

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget


class SOOTCallGraphReader(AbstractCallGraphReader):
    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        """
        A SOOT line looks like:
        <java.lang.System: void checkKey(java.lang.String)>	$z0 = virtualinvoke r0.<java.lang.String: boolean isEmpty()>() (java/lang/System:1047)	null	<java.lang.String: boolean isEmpty()>	null

        @param line: The line in the TSV file produced by SootInterface
        @return: The corresponding CGCallSite and CGMethod
        """

        tokens = line.split('\t')
        callsite_toks = tokens[1].split(' ')[-1].strip('()').split(':')  # Gets the part in parens
        callsite = CGCallSite(callsite_toks[0], callsite_toks[1], tokens[2])
        target_regex = re.compile("<(.*?): (.*?) (.*?)\((.*?)\)>")
        target_matches = target_regex.match(tokens[-2])
        target = CGTarget(target_matches.group(1), target_matches.group(2), target_matches.group(3), tokens[-1],
                          *(target_matches.group(4).split(',')))
        return callsite, target
