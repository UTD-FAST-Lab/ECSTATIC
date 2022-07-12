from src.ecstatic.toolreverter.BinarySearch import BinarySearch
import os

from src.ecstatic.toolreverter.Reverter import ReverterFactory

reverter = ReverterFactory().get_reverter("wala","v1.5.5","v1.5.7")

class B:
    def __init__(self):
        self.violated="true"

b=B();

BinarySearch(reverter.GITREPO,reverter.FROM_TAG,reverter.TO_TAG,[b],"","","").performsearch()

