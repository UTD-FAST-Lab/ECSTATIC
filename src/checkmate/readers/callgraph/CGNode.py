class CGNode:

    def __init__(self, content: str, site: str, context: str):
        self.content = str(content).strip()
        self.site = str(site).strip()
        self.context = str(context).strip()

    def __eq__(self, other):
        return isinstance(other, CGNode) and self.content == other.content and self.context == other.context \
    and self.site == other.site

    def __hash__(self):
        return hash((self.content, self.context))

    def __str__(self):
        return f'Content: {self.content} Context: {self.context}'