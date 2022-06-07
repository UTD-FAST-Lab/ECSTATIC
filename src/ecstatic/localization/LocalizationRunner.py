import os
import sys


#Class that runs a localization algorithm and handles results
class LocalizationRunner():

    #No Choice for now
    def __init__(self):
        #STUB
    def handle_results(self,results):
        #TODO:: this is not correct, the result dir can change
        os.mkdir("/results/localization")
        for x in results:
            #make a file
            filename = "/results/localization";
            filename+="/"+x.partial_orders+"/"+x.apk+".localize.result"
            with open(filename,'w') as fp:
                fp.write(x.result)
    def runLocalizerHandleResult(self):
        localize_results = self.localization.localize();
        handle_results(localize_results);

    def setLocalizer(self, localizer: AbstractLocalization):
        self.localization = localizer;
