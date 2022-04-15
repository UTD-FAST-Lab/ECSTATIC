from json import JSONEncoder


class CGCallSite():
    def __init__(self, clazz: str, line_number: int, context: str):
        self.clazz = clazz
        self.line_number = line_number
        self.context = context

    def __hash__(self):
        return hash((self.clazz, self.line_number))

    def __eq__(self, other):
        return isinstance(other, CGCallSite) and self.clazz == other.clazz and self.line_number == other.line_number

    def __str__(self):
        return f'{self.clazz}:{self.line_number}'
