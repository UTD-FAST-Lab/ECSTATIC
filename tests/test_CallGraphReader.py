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


import importlib.resources

from networkx import DiGraph

from src.ecstatic.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.ecstatic.readers.callgraph.DOOPCallGraphReader import DOOPCallGraphReader


def test_wala_contextins():
    wr = AbstractCallGraphReader()
    graph: DiGraph = wr.import_file(importlib.resources.path('tests.resources.callgraphs.wala', 'insenscallgraph.tsv'))
    assert len(graph.edges) == 101

def test_wala_contextsens():
    wr = AbstractCallGraphReader()
    graph : DiGraph = wr.import_file(importlib.resources.path('tests.resources.callgraphs.wala', 'contextsenscallgraph.tsv'))
    assert len(graph.edges) == 1226

def test_wala_objsens():
    wr = AbstractCallGraphReader()
    graph: DiGraph = wr.import_file(importlib.resources.path('tests.resources.callgraphs.wala', 'objsenscallgraph.tsv'))
    assert len(graph.edges) == 147

def test_soot_callgraph():
    sr = AbstractCallGraphReader()
    graph: DiGraph = sr.import_file(importlib.resources.path('tests.resources.callgraphs.soot', 'soot_callgraph_spark.tsv'))
    assert len(graph.edges) == 96682

def test_doop_contextins():
    dr = DOOPCallGraphReader()
    graph: DiGraph = dr.import_file(importlib.resources.path('tests.resources.callgraphs.doop', 'doop_contextinsensitive.csv'))
    assert len(graph.edges) == 49877