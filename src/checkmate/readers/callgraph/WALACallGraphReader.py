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
        callsite = tokens[0].split(',')[1]
        callsite = CGCallSite(callsite.split(':')[0], callsite.split(':')[1], tokens[2])
        java_signature_regex = re.compile(r"(.*?).([A-z_\-]*?)\((.*?)\)(.*)")
        matches = java_signature_regex.match(tokens[3])
        target = CGTarget(matches.group(1), matches.group(2),
                          self.parse_type(matches.group(4)),
                          [self.parse_type(t) for t in matches.group(3).split(';')],
                          tokens[4])
        return callsite, target

    def parse_type(self, type: str) -> str:
        postfix = ""
        for charix in range(len(type)):
            if type[charix] == '[':
                postfix = postfix + "[]"
            elif type[charix] == "L":
                return type[charix + 1:].strip(";") + postfix
            else:
                return self.map_character_to_type(type[charix])

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
