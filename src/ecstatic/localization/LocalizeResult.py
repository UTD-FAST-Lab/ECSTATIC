from src.ecstatic.util.PartialOrder import PartialOrder
from typing import List, Set
class LocalizeResult():

    def __init__(self, result: List[str], apk: str, partial_orders: Set[PartialOrder]):

        self.result=result;
        self.apk=apk;
        self.partial_orders=partial_orders;
