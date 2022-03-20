from typing import Dict

from networkx import DiGraph

from src.checkmate.readers.callgraph.CGNode import CGNode


def out_edges(graph: DiGraph) -> Dict[CGNode, int]:
    return {k: len(v) for k, v in graph.adjacency()}
