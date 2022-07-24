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
                else:
                    parts = []
                    node = []
                    try:
                        parts = i.strip().split(" ")
                        node = parts[2].strip(" label=").strip('"]').strip('"]}').split("\\n")
                    except:
                        parts = i.strip().split(" ")
                    nodes[parts[0]] = node
        for j in edges:
            callid, targetid = j
            call_funct = nodes[callid][0]
            if (nodes[callid] != ['<main>']):
                path_array = nodes[callid][1].split("/")
                call_location = path_array[-1]
            else:
                call_location = ''
            target_funct = nodes[targetid][0]
            target_path_array = nodes[targetid][1].split("/")
            target_location = target_path_array[-1]
            # add tuple of CGCallsite and CGTarget to list
            callsite = CGCallSite(call_funct, callid, '')
            target = CGTarget(targetid, '')
            callgraph.append((callsite, target))
        return callgraph