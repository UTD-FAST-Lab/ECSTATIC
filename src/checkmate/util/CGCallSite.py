from json import JSONEncoder


class CGCallSite():
    def __init__(self, clazz: str, stmt: str, context: str):
        self.clazz = clazz
        self.stmt = stmt
        self.context = context

    def __hash__(self):
        return hash((self.clazz, self.stmt))

    def __eq__(self, other):
        return isinstance(other, CGCallSite) and self.clazz == other.clazz and self.stmt == other.stmt

    def as_dict(self):
        return {'caller': self.clazz,
                'callsite': self.callsite,
                'context': self.context}
