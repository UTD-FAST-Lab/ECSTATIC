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
    def getUnion(self,dict1,dict2):
        rDict=dict();
        for x in [*dict1]:
            rDict[x] = dict1[x];
            if(x in dict2):
                rDict[x] = rDict[x]+dict2[x];
            else:
                rDict[x] = dict2[x];

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

    def handle_union(self,results):
        resultMaps =dict()
        for x in results:
            pOString = str(x.partial_order)
            resultDict = x.fDict;
            if resultsMap.get(pOString) is not None:
                resultsMap[pOString] = self.getUnion(resultDict,resultsMap[pOString])
            else:
                resultsMap[pOString] = resultDict;
        for x in results:
            pOString = str(x.partial_order)
            resultDict = x.fragmentation;
            if fragmentMap.get(pOString) is not None:
                #we've seen this pO before
                fragmentMap[pOString] = self.getUnion(resultDict,fragmentMap[pOString]);
            else:
                #fresh
                fragmentMap[pOString] = resultDict;
        return resultsMap,fragmentMap;
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
        fragmentMap = dict();
        for x in results:
            pOString = str(x.partial_order)
            resultDict = x.fragmentation;
            if fragmentMap.get(pOString) is not None:
                #we've seen this pO before
                fragmentMap[pOString] = self.getIntersection(resultDict,fragmentMap[pOString]);
            else:
                #fresh
                fragmentMap[pOString] = resultDict;
        for x in [*resultsMap]:
            fName = "/results/localization/"+x+"/"+x+".intersect";
            with open(fName,'w') as fp:
                for line in [*resultsMap[x]]:
                    fp.write(line.strip()+":"+str(resultsMap[x][line]).strip()+"\n")
        for x in [*fragmentMap]:
            fName = "/results/localization/"+x+"/"+x+".fragintersect";
            with open(fName,'w') as fp:
                for line in [*fragmentMap[x]]:
                    fp.write(line.strip()+":"+str(fragmentMap[x][line]).strip()+"\n")
        return resultsMap,fragmentMap;

    def handle_results(self,results):
        #TODO:: this is not correct, the result dir can change
        if(not os.path.exists("/results/localization")):
            os.mkdir("/results/localization")

        for x in results:
            #make a file
            filename = "/results/localization";
            csvfile = "/results/localization/"+str(x.partial_order)+"/"+str(x.partial_order)+".csv"
            if not os.path.exists("/results/localization/"+str(x.partial_order)):
                os.mkdir("/results/localization/"+str(x.partial_order));
            if not os.path.exists(csvfile):
                with open(csvfile,'w') as fp:
                    fp.write("APK,diff_size,fragment_size\n")
            filename+="/"+str(x.partial_order)+"/"+x.apk+".localize.result"
            filename2 =  filename+".fragmentation"
            with open(filename,'w') as fp:
                fp.write(x.result+"\n")
            with open(filename2,'w') as fp:
                fp.write(x.get_fragmentation())
            with open(csvfile,'a') as fp:
                fp.write(x.apk+","+str(len(x.result.split("\n")))+","+str(len([*x.fragmentation]))+"\n")
        intersectMap,fragmentMap = self.handle_intersection(results);
        unionMap,uFragmentMap = self.handle_union(results);
        filename="/results/localization/po_intersects.csv"
        with open(filename,'w') as fp:
            fp.write("PartialOrder,diff_intersect,diff_union,fragment_intersect,fragment_union\n")
            for x in [*intersectMap]:
                fp.write(x+","+str(len(intersectMap[x]))+","+str(len(unionMap[x]))+","+str(len(fragmentMap[x]))+","+str(len(uFragmentMap[x]))"\n")
    def runLocalizerHandleResult(self):
        localize_results = self.localization.localize();
        self.handle_results(localize_results);

    def setLocalizer(self, localizer: AbstractLocalization):
        self.localization = localizer;
