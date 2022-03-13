class CGNode:

    def __init__(self, content: str, context: str):
        self.content = content
        self.context = context

    def __eq__(self, other):
        return isinstance(other, CGNode) and self.content == other.content and self.context == other.context

    def __hash__(self):
        return hash((self.content, self.context))

    def __str__(self):
        return f'Content: {self.content} Context: {self.context}'