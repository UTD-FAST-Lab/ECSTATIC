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


    
