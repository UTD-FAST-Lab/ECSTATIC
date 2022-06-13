from src.ecstatic.localization.AbstractLocalization import AbstractLocalization;
from src.ecstatic.localization.DiffLocalizer import DiffLocalizer;
from src.ecstatic.localization.LocalizationRunner import LocalizationRunner;
import os
class testresult:
    def __init__(self,pO,dicti,violated):
        self.partial_order=pO;
        self.fDict=dicti;
        self.violated=violated;

localize = DiffLocalizer(None);
runner = LocalizationRunner();
pO1 = "B"
pOV1 = True;
pO1D = dict();

pO1D["line1"] = 1;
pO1D["line2"] = 1;
pO1D["line3"] = 1;
pO1D["line4"] = 1;
pO1D["line5"] = 1;
pO1D["line6"] = 1;


pO2 = "A"
pOV2 = False;
pO2D = dict();
pO2D["line1"] = 1;
pO2D["line2"] = 2;
pO2D["line3"] = 1;
pO2D["line4"] = 2;

testA = testresult(pO1,pO1D,pOV1);
testB = testresult(pO2,pO2D,pOV2);
results = []
results.append(testA);
results.append(testB);

pO1 = "A"
pOV1 = True;
pO1D = dict();

pO1D["line1"] = 1;
pO1D["line4"] = 1;
pO1D["line5"] = 1;
pO1D["line6"] = 1;

testC = testresult(pO1,pO1D,pOV1);
results.append(testC);



runner.handle_results(results);
