from typing import Set, Dict, List

from networkx import DiGraph

from src.checkmate.readers.callgraph.CGNode import CGNode


def to_context_insensitive(graph: DiGraph) -> DiGraph:
    new_graph = DiGraph()
    for u, v in graph.edges:
        u: CGNode
        v: CGNode
        u_prime = CGNode(u.content, None)
        v_prime = CGNode(v.content, None)
        new_graph.add_edge(u_prime, v_prime)
    return new_graph

def call_site_to_targets(graph: DiGraph) -> Dict[str, Set[str]]:
    result: Dict[str, Set[str]] = dict()
    for caller, targets in graph.adjacency():
        caller: CGNode
        targets: List[CGNode]
        if caller.site not in result:
            result[caller.site] = set()
        result[caller.site].update([k.content for k in targets])
    return result