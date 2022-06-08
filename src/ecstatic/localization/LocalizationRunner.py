import os
import sys
from src.ecstatic.localization.AbstractLocalization import AbstractLocalization;

#Class that runs a localization algorithm and handles results
class LocalizationRunner():

    #No Choice for now
    def __init__(self):
        #STUB
        print("")

    def getIntersection(self, dict1, dict2):
        rDict=dict();

        for x in [*dict1]:
            if x in dict2:
                rDict[x] = dict1[x]+dict2[x]

        return rDict;

    def turnDiffStringIntoDict(self, diffString):
        rDict= dict()
        for x in diffString.split("\n"):
            lineSp= x.split(":")
            line = lineSp[0]+":"+lineSp[1];
            lineCount = int(lineSp[2])
            if rDict.get(line) is not None:
                #we've seen before
                rDict[line] = rDict[line]+lineCount;
            else:
                rDict[line] = lineCount;
        return rDict;

    def handle_intersection(self,results):
        #method that returns set intersection of all apks that recreated this partial order violation
        resultsMap = dict()
        for x in results:
            pOString = str(x.partial_order)
            resultDict = x.fDict;
            if resultsMap.get(pOString) is not None:
                #we've seen this pO before
                resultsMap[pOString] = self.getIntersection(resultDict,resultsMap[pOString]);
            else:
                #fresh
                resultsMap[pOString] = resultDict;

        for x in [*resultsMap]:
            fName = "/results/localization/"+x+"/"+x+".intersect";
            with open(fName,'w') as fp:
                for line in [*resultsMap[x]]:
                    fp.write(line.strip()+":"+str(resultsMap[x][line]).strip()+"\n")

    def handle_results(self,results):
        #TODO:: this is not correct, the result dir can change
        if(not os.path.exists("/results/localization")):
            os.mkdir("/results/localization")
        for x in results:
            #make a file
            filename = "/results/localization";
            if not os.path.exists("/results/localization/"+str(x.partial_order)):
                os.mkdir("/results/localization/"+str(x.partial_order));
            filename+="/"+str(x.partial_order)+"/"+x.apk+".localize.result"
            filename2 =  filename+".fragmentation"
            with open(filename,'w') as fp:
                fp.write(x.result+"\n")
            with open(filename2,'w') as fp:
                fp.write(x.get_fragmentation())

        self.handle_intersection(results);
    def runLocalizerHandleResult(self):
        localize_results = self.localization.localize();
        self.handle_results(localize_results);

    def setLocalizer(self, localizer: AbstractLocalization):
        self.localization = localizer;
