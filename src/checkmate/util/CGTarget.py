from dataclasses import dataclass


@dataclass(eq=False, unsafe_hash=False)
class CGTarget:
    target: str
    context: str

    def __hash__(self):
        return hash(self.target)

    def __eq__(self, other):
        return isinstance(other, CGTarget) and self.target == other.target

    def as_dict(self):
        return {'target': self.target,
                'context': self.context}
