from src.ecstatic.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.ecstatic.util.CGCallSite import CGCallSite
from src.ecstatic.util.CGTarget import CGTarget

from abc import ABC
from typing import Tuple, List, Any

class TAJSCallGraphReader(AbstractCallGraphReader):
    def import_file(self, file):
        callgraph: List[Tuple[Any, Any]] = []
        edges = []
        nodes = {}
        with open(file) as f:
            lines = f.readlines()
            for i in lines:
                # print(i)
                if "->" in i:
                    parts = i.strip().split(" -> ")
                    edges.append((parts[0], parts[1]))
                    print("edge:", i)
                else:
                    parts = []
                    node = []
                    try:
                        parts = i.strip().split(" ")
                        node = parts[2].strip(" label=").strip('"]').strip('"]}').split("\\n")
                    except:
                        parts = i.strip().split(" ")
                    nodes[parts[0]] = node
                    print("node:", i)
        for j in edges:
            callid, targetid = j
            call_funct = nodes[callid][0]
            if (nodes[callid] != ['<main>']):
                call_location = nodes[callid][1]
            else:
                call_location = ''
            target_funct = nodes[targetid][0]
            target_location = nodes[targetid][1]
            # add tuple of CGCallsite and CGTarget to list
            callsite = CGCallSite(call_funct, call_location, '')
            target = CGTarget(target_location, '')
            print(call_funct, call_location, target_location)
            callgraph.append((callsite, target))
        return callgraph