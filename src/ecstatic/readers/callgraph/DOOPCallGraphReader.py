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
from dataclasses import dataclass, field

import regex as re
from typing import Tuple

from src.ecstatic.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.ecstatic.util.CGCallSite import CGCallSite
from src.ecstatic.util.CGTarget import CGTarget

logger = logging.getLogger(__name__)

@dataclass(unsafe_hash=True)
class DoopCallgraphCaller:
    content: str
    context: str = field(compare=False)

@dataclass(unsafe_hash=True)
class DoopCallgraphTarget:
    content: str
    context: str = field(compare=False)

class DOOPCallGraphReader(AbstractCallGraphReader):
    """
    A DOOP line is [<<immutable-context>>] <sun.security.x509.AVA: void <clinit>()>/java.security.AccessController.doPrivileged/0  [<<immutable-context>>] <java.security.AccessController: j\
ava.lang.Object doPrivileged(java.security.PrivilegedAction)>
    """

    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        line = line.strip()
        toks = line.split('\t')
        if len(toks) == 4:
            return (CGCallSite(context=toks[0], clazz=toks[1].split('/')[0].strip("<>"), stmt="/".join(toks[1].split('/')[1:])),
                              CGTarget(context=toks[2], target=toks[3]))
        else:
            logger.critical(f"DOOPReader could not read line ({line})")
            return None


