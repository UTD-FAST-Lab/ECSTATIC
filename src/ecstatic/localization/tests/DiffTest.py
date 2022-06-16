from src.ecstatic.localization.DiffLocalizer import DiffLocalizer
import json
from pprint import pprint
localize = DiffLocalizer(None);
pO="A->B"
obj = localize.get_diff_for_files("a.apk.xml.flowdroid.result.instrumentation",
                                  "b.apk.xml.flowdroid.result.instrumentation",pO, "a.apk")

print(obj.result)
print(obj.fragmentation)
