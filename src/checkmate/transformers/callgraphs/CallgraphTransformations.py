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
