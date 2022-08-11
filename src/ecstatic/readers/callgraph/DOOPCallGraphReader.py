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
class DoopCallGraphCaller:
    caller: str
    caller_context: str = field(default="", compare=False)


@dataclass(unsafe_hash=True)
class DoopCallGraphTarget:
    target: str
    target_context: str = field(default="", compare=False)


class DOOPCallGraphReader(AbstractCallGraphReader):
    """
    A DOOP line is [<<immutable-context>>] <sun.security.x509.AVA: void <clinit>()>/java.security.AccessController.doPrivileged/0  [<<immutable-context>>] <java.security.AccessController: j\
ava.lang.Object doPrivileged(java.security.PrivilegedAction)>
    """

    pattern = re.compile("^\[(.*?(?<!\[))\]\s*?(.*?)\[(.*?(?<!\[))\]\s*(.*)$")

    def process_line(self, line: str) -> Tuple[DoopCallGraphCaller, DoopCallGraphTarget]:
        line = line.strip()
        if ma := re.fullmatch(DOOPCallGraphReader.pattern, line):
            return (DoopCallGraphCaller(caller=ma.group(2), caller_context=ma.group(1)),
                    DoopCallGraphTarget(target=ma.group(4), target_context=ma.group(3)))
        else:
            logger.critical(f"DOOPReader could not read line ({line})")
            return None


