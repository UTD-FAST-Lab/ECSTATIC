from src.ecstatic.util.PartialOrder import PartialOrder
from typing import List, Set
class LocalizeResult():

    def __init__(self, result: str, apk: str, partial_order: PartialOrder, fragmentation, fDict):

        self.result=result;
        self.apk=apk;
        self.partial_order=partial_order;
        self.fragmentation=fragmentation;
        self.fDict = fDict;

    def get_fragmentation(self):
        rString="";
        for x in [*self.fragmentation]:
            rString+=x.strip()+":"+str(self.fragmentation[x])+"\n";
        return rString;
