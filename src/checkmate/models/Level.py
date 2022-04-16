from dataclasses import field, dataclass

@dataclass
class Level:
    option_name: str
    level_name: str

    def __str__(self):
        return f"{self.option_name}.{self.level_name}"
