from src.ecstatic.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.ecstatic.util.CGCallSite import CGCallSite
from src.ecstatic.util.CGTarget import CGTarget

from abc import ABC
from typing import Tuple, List, Any

class TAJSCallGraphReader(AbstractCallGraphReader):
    def import_file(self, file):
        callgraph: List[Tuple[CGCallSite, CGTarget]] = []
        edges = []
        nodes = {}
        with open(file) as f:
            lines = f.readlines()
            for i in lines:
                # print(i)
                if "->" in i:
                    parts = i.strip().split(" -> ")
                    edges.append((parts[0], parts[1]))
                else:
                    parts = []
                    node = []
                    try:
                        parts = i.strip().split(" ")
                        node = parts[2].strip(" label=").strip('"]').split("\\n")
                        print(node)
                    except:
                        parts = i.strip().split(" ")
                    nodes[parts[0]] = node
        for j in edges:
            callid, targetid = j
            if (nodes[callid] != ['<main>"]}']):
                call_funct = nodes[callid][0]
                call_location = nodes[callid][1]
                target_funct = nodes[targetid][0]
                target_location = nodes[targetid][1]
            # Need to change setting of callsite and target below
            callsite = CGCallSite(call_funct, call_location, '')
            target = CGTarget(target_funct, '')
            callgraph.append((callsite, target))
            # add tuple of CGCallsite and CGTarget to list
        return callgraph