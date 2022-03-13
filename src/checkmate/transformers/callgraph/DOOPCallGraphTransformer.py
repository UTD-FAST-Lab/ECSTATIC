import re

from networkx import DiGraph

from src.checkmate.transformers.callgraph.AbstractCallGraphTransformer import AbstractCallGraphTransformer
from src.checkmate.transformers.callgraph.CGNode import CGNode


class DOOPCallGraphTransformer(AbstractCallGraphTransformer):
    def import_graph(self, file: str) -> DiGraph:
        new_g: DiGraph = DiGraph()
        with open(file) as f:
            lines = [l.strip() for l in f.readlines()]
        for l in lines:
            groups = re.match(r"\[(.+?)\]\s(.+?)\[(.+?)\]\s(.+)", l)
            new_g.add_edge(CGNode(*groups.group(2, 1)), CGNode(*groups.group(4, 3)))
        return new_g
