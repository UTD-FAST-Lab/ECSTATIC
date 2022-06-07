import os
import sys
from src.ecstatic.localization.AbstractLocalization import AbstractLocalization;

#Class that runs a localization algorithm and handles results
class LocalizationRunner():

    #No Choice for now
    def __init__(self):
        #STUB
        print("")

    def handle_results(self,results):
        #TODO:: this is not correct, the result dir can change
        if(not os.path.exists("/results/localization")):
            os.mkdir("/results/localization")
        for x in results:
            #make a file
            filename = "/results/localization";
            i=0;
            for pO in x.partial_orders:
                if not os.path.exists("/results/localization/"+str(pO)):
                    os.mkdir("/results/localization/"+str(pO));
                filename+="/"+str(pO)+"/"+x.apk+".localize.result"
                with open(filename,'w') as fp:
                    fp.write(x.result[i]+"\n")
                i+=1;
    def runLocalizerHandleResult(self):
        localize_results = self.localization.localize();
        self.handle_results(localize_results);

    def setLocalizer(self, localizer: AbstractLocalization):
        self.localization = localizer;
