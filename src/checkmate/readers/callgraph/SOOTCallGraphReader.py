import logging
import re
import sre_compile
from typing import Tuple

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget


class SOOTCallGraphReader(AbstractCallGraphReader):
    logger = logging.getLogger("AbstractCallGraphReader")

    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        """
        A SOOT line looks like:
        <java.lang.System: void checkKey(java.lang.String)>	$z0 = virtualinvoke r0.<java.lang.String: boolean isEmpty()>() (java/lang/System:1047)	null	<java.lang.String: boolean isEmpty()>	null

        @param line: The line in the TSV file produced by SootInterface
        @return: The corresponding CGCallSite and CGMethod
        """

        try:
            tokens = line.split('\t')
            callsite = CGCallSite(tokens[0], tokens[1], tokens[2])
            target = CGTarget(tokens[3], context=tokens[4]),
            return callsite, target
        except IndexError as ie:
            SOOTCallGraphReader.logger.exception(f'Tried to parse line {line}')

