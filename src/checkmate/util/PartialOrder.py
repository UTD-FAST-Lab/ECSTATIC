from dataclasses import dataclass
from enum import Enum

from src.checkmate.models.Level import Level


class PartialOrderType(Enum):
    MORE_PRECISE_THAN = 'is more precise than'
    MORE_SOUND_THAN = 'is more sound than'


@dataclass
class PartialOrder:
    left: Level
    type: PartialOrderType
    right: Level

    def __hash__(self):
        return hash((self.left, self.type, self.right))

    def __str__(self):
        return f'{str(self.left)} {self.type} {str(self.right)}'
