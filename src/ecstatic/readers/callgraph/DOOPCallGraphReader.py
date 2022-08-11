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
import re
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
        line = line.strip()
        if ma := re.fullmatch("^\[(.*)\]\s*<(.*?)>/(.*?)/?\d\s*\[(.*?)\]\s*<(.*)>$", line):
            return (CGCallSite(context=ma.group(1), clazz=ma.group(2), stmt=ma.group(3)),
                    CGTarget(context=ma.group(4), target=ma.group(5)))
        else:
            raise ValueError(f"DOOPReader could not read line ({line})")
