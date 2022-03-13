import re
from typing import Tuple

import networkx.drawing.nx_pydot
from networkx import DiGraph, MultiDiGraph

from src.checkmate.transformers.callgraph.AbstractCallGraphTransformer import AbstractCallGraphTransformer
from src.checkmate.transformers.callgraph.CGNode import CGNode


class WALACallGraphTransformer(AbstractCallGraphTransformer):
    def import_graph(self, file: str) -> DiGraph:
        g: MultiDiGraph = networkx.drawing.nx_pydot.read_dot(file)
        new_g: DiGraph = DiGraph()
        for u, v in g.edges():
            def get_node_and_context(input: str) -> Tuple[str, str]:
                groups = re.match(r"Node:(.*?)Context:(.*)", input)
                return groups.group(1, 2)
            new_g.add_edge(CGNode(*get_node_and_context(u)), CGNode(*get_node_and_context(v)))
        return new_g

