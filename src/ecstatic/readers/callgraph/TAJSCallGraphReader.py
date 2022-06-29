import re

def import_file(file):
    # callgraph: List[Tuple[CGCallSite, CGTarget]] = []
    callgraph = []
    edges = []
    nodes = {}
    with open(file) as f:
        lines = f.readlines()
        for i in lines:
            #print(i)
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
                #print(re.search('label=\"(.*)\"', i))
                ## separate id, class??, and statement??
                
                ## split on \n
                ## submit context 
                pass
    for j in edges:
        callid, targetid = j
        if (nodes[callid] != ['<main>"]}']):
            callfunct = nodes[callid][0]
            calllocation = nodes[callid][1]
            calltarget = nodes[targetid][0]
            print(callfunct, calllocation, calltarget)

        ## create CGCallsite (callclass, callstatement, ??context??)
        ## create CGTarget (callclass, callstatement, ??context??)
        ## add tuple of CGCallsite and CGTarget to list
        


            

import_file("C:/Users/egsch/Documents/callgraph.dot")