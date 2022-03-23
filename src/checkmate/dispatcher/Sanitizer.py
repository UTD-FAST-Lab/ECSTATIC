import os
from importlib.resources import path
import logging
import json

with path('src.resources', 'tools') as tools_dir:
    tools = [t for t in os.listdir(tools_dir) if os.path.isdir(os.path.join(tools_dir, t))]

with path('src.resources', 'benchmarks') as benchmarks_dir:
    benchmarks = [b for b in os.listdir(benchmarks_dir) if os.path.isdir(os.path.join(benchmarks_dir, b))]

tasks = ['cg', 'taint']

def sanity_check(tool, benchmarks, tasks):
    comp_json = os.path.join(tools_dir, tool, 'compatibility.json');
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


    
