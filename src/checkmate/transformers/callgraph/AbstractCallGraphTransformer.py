from abc import ABC, abstractmethod
from networkx import DiGraph


class AbstractCallGraphTransformer(ABC):

    def transform(self, input_file: str, output_file: str):
        self.write_graph(self.import_graph(input_file), output_file)

    @abstractmethod
    def import_graph(self, file: str) -> DiGraph:
        pass

    def write_graph(self, graph: DiGraph, output_file: str):
        with open(output_file, 'w') as f:
            f.write('node1\tnode2\n')
            for u, v in graph.edges:
                f.write(f'{str(u)}\t{str(v)}\n')
