from typing import Tuple

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget


class WALACallGraphReader(AbstractCallGraphReader):
    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        """
        A WALA line looks like:

        < Primordial, Lsun/reflect/generics/reflectiveObjects/TypeVariableImpl, hashCode()I >	invokevirtual < Primordial, Ljava/lang/Object, hashCode()I >@4	Everywhere	synthetic < Primordial, Ljava/lang/Object, hashCode()I >	Everywhere
        @param line:
        @return:
        """

        pass

    def map_character_to_type(self, character: str) -> str:
        types = {
            'B': 'byte',
            'C': 'char',
            'D': 'double',
            'F': 'float',
            'I': 'int',
            'J': 'long',
            'S': 'short',
            'Z': 'boolean'
        }
        return types[character]