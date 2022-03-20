from abc import ABC, abstractmethod
from typing import Tuple

from networkx import DiGraph

from src.checkmate.readers.callgraph.CGNode import CGNode


class AbstractCallGraphReader(ABC):

    def import_graph(self, file: str) -> DiGraph:
        callgraph = DiGraph()
        with open(file) as f:
            lines = f.readlines()
        for l in lines[1:]: # skip header line
            callgraph.add_edge(*self.__process_line(self.__transform(l)))
        return callgraph

    @abstractmethod
    def __transform(self, line: str) -> str:
        return line

    """
    Creates call graph nodes from input line.
    Expects line to have the following format:
    caller\tcallsite\tcalling_context\ttarget\ttarget_context
    """
    def __process_line(self, line: str) -> Tuple[CGNode, CGNode]:
        tokens = line.split('\t')
        caller = CGNode(f'{tokens[0]} {tokens[1]}', tokens[2])
        target = CGNode(tokens[3], tokens[4])
        return caller, target