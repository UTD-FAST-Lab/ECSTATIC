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


from typing import Set, Dict, List

from networkx import DiGraph

from src.ecstatic.readers.callgraph.CGNode import CGNode


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
        full_call_site = f"{caller.content}:{caller.site}"
        if full_call_site not in result:
            result[full_call_site] = set()
        result[full_call_site].update([k.content for k in targets])
    return result