import logging
import re
from typing import Tuple

from networkx import DiGraph

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.readers.callgraph.CGNode import CGNode
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget

logger = logging.getLogger(__name__)

class DOOPCallGraphReader(AbstractCallGraphReader):
    pass