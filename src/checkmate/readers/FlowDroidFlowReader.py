from typing import Iterable
import xml.etree.ElementTree as ElementTree

from src.checkmate.models.Flow import Flow
from src.checkmate.readers.AbstractReader import AbstractReader


class FlowDroidFlowReader(AbstractReader):

    def import_file(self, file: str) -> Iterable[Flow]:
        return [Flow(f) for f in ElementTree.parse(file).getroot().find('flows').findall('flow')]
