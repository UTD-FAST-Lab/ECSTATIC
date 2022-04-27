from abc import ABC, abstractmethod
from typing import Any


class AbstractReader(ABC):

    @abstractmethod
    def import_file(self, file: str) -> Any:
        pass