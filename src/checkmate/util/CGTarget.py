from typing import List, Tuple


class CGTarget:

    def __init__(self, clazz: str, name: str, return_type: str, context: str, params: List[str]):
        self.clazz = clazz
        self.name = name
        self.return_type = return_type
        self.context = context
        self.params = params

    def __eq__(self, other):
        return isinstance(other, CGTarget) and \
               self.clazz == other.clazz and \
               self.name == other.name and \
               self.return_type == other.return_type and \
               self.params == other.params

    def __str__(self):
        return f'{self.clazz}: {self.return_type} {self.name}{self.params}'

    def __hash__(self):
        return hash((self.clazz, self.name, self.return_type, self.params))
