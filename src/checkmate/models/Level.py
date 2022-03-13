class Level:
    """A single level of an option"""
    def __init__(self, option_name, level_name):
        self.option_name = option_name
        self.level_name = level_name
        
    def __eq__(self, o1):
        return isinstance(o1, Level) and\
            o1.option_name == self.option_name and\
            o1.level_name == self.level_name

    def __hash__(self):
        return hash((self.option_name, self.level_name))

    def __str__(self):
        return f"{self.option_name}.{self.level_name}"
