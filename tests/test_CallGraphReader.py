import importlib.resources

from networkx import DiGraph

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.readers.callgraph.DOOPCallGraphReader import DOOPCallGraphReader
from src.checkmate.transformers.callgraphs import CallgraphTransformations


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