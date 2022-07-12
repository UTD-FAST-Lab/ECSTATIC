#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


import logging
from typing import Tuple

from src.ecstatic.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.ecstatic.util.CGCallSite import CGCallSite
from src.ecstatic.util.CGTarget import CGTarget

logger = logging.getLogger(__name__)


class DOOPCallGraphReader(AbstractCallGraphReader):
    """
    A DOOP line is [<<immutable-context>>] <sun.security.x509.AVA: void <clinit>()>/java.security.AccessController.doPrivileged/0  [<<immutable-context>>] <java.security.AccessController: j\
ava.lang.Object doPrivileged(java.security.PrivilegedAction)>
    """
    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        tokens = line.split("\t")
        if len(tokens) == 5:
            return super().process_line(line)
        else:
            return (CGCallSite(clazz=tokens[1].split('/')[0].strip(' <>'),
                               stmt='/'.join(tokens[1].split('/')[1:]),
                               context=tokens[0]),
                    CGTarget(tokens[3], tokens[2]))
