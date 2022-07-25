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

class WALACallGraphReader(AbstractCallGraphReader):

    def process_line(self, line: str) -> Tuple[CGCallSite, CGTarget]:
        """
        Example of WALA line is < Application, Lcfne/Demo, main([Ljava/lang/String;)V >	invokestatic < Application, Ljava/lang/Class, forName(Ljava/lang/String;)Ljava/lang/Class; >@2	Everywhere	java.lang.Class.forName(Ljava/lang/String;)Ljava/lang/Class;	Everywhere

        Parameters
        ----------
        line

        Returns
        -------

        """
        if not line.startswith("< Application"):
            logger.info(f"Skipping line {line}")
            return None
        tokens = line.split("\t")
        cs = CGCallSite(clazz=f"{tokens[0].split(',')[1].strip()[1:].replace('/', '.')}.{tokens[0].split(',')[2].strip(' <>')}",
                        stmt = re.sub(r"@\d*$", "", tokens[1]), context=tokens[2])
        logging.info(f"Replaced {tokens[1]} with {cs.stmt}")
        tar = CGTarget(target=tokens[3], context=tokens[4])
        logging.debug(f"Processed {line} to {(cs, tar)}")
        return cs, tar
