import os
import importlib
import logging
import json

tools_dir = importlib.resources.path('src.resources', 'tools')
tools = [t for t in os.lsdir(tools_dir) if os.path.isdir(os.path.join(tools_dir, t))]

benchmarks_dir = importlib.resources.path('src.resources', 'benchamrks')
benchmarks = [b for b in os.lsdir(benchmarks_dir) if os.path.isdir(os.path.join(benchmarks_dir, b))]

tasks = ['cg', 'taint']

def sanity_check(tool, benchmarks, tasks):
    comp_json = os.path.join(tools_dir, 'compatibility.json');
    if not os.path.exists(comp_json):
        logging.error(f'compatibility.json not found for tool {tool}')
        exit(0)

    with open(comp_json, 'r') as f:
        jdata = json.load(f)

    comp_benchmarks = []
    for b in benchmarks:
        if b not in jdata['bechmarks']:
            logging.warning(f'tool {tool} and benchmark {b} are not compatible, {b} will be skipped')
        else:
            comp_benchmarks.append(b)

    comp_tasks = []
    for t in tasks:
        if t not in jdata['tasks']:
            logging.warning(f'tool {tool} and task {t} are not compatible, {t} will be skipped')
        else:
            comp_tasks.append(t)

    return comp_benchmarks, comp_tasks


    
