from dataclasses import dataclass
from json import JSONEncoder

@dataclass
class CGCallSite():
    clazz: str
    stmt: str
    context: str

    def __hash__(self):
        return hash((self.clazz, self.stmt))

    def __eq__(self, other):
        return isinstance(other, CGCallSite) and self.clazz == other.clazz and self.stmt == other.stmt