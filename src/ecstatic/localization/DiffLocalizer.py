import sys
import os
import json
import logging
from src.ecstatic.localization.AbstractLocalization import AbstractLocalization;
from src.ecstatic.localization.LocalizeResult import LocalizeResult;

class DiffLocalizer(AbstractLocalization):


    def __init__(self,violations):
        self.violations=violations;

    def get_dict_for_file(self,file_lines):
        rDict = dict()
        for x in file_lines:
            line = x.split(":")
            if rDict.get(line[1]) is not None:
                #we've seen this class before inc count
                rDict[line[1]] = rDict[line[1]]+1
            else:
                rDict[line[1]] = 1;
        return rDict;
    def get_diff_for_files(self,file1,file2,partial_orders):
        f1_lines = []
        f2_lines = []
        with open(file1,'r') as fp:
            f1_lines = fp.readlines()
        with open(file2,'r') as fp:
            f2_lines = fp.readlines()

        f1_dict = self.get_dict_for_file(f1_lines)
        f2_dict = self.get_dict_for_file(f2_lines)

        rList = []
        #TODO::.keys method
        f1_lines = [*f1_dict]
        f2_lines = [*f2_dict]
        # 1 -> 2, A -> B

        diffInfo="";
        for x in f2_lines:
            if x not in f1_lines:
                diffInfo+=x+":"+f2_dict[x]+"\n";
        rList.append(diffInfo);
        diffInfo2="";
        if len(partial_orders) > 1:
            for x in f1_lines:
                if x not in f2_lines:
                    diffInfo2+=x+":"+f1_dict[x]+"\n"
            rList.append(diffInfo2);

        return rList;


    def localize(self):
        #Internal logic for running this localizer
        logging.warning("Started Localize")
        #go through all violations and check em out
        rList: List[LocalizeResult] = []
        for x in self.violations:
            #we are interested in a couple things, mostly
            # the apk
            # the two files that contain instrumentation info
            # the partial_orders being bad
            target = x.job1.job.target.name
            target = target[target.rindex("/")+1:];

            job1 = x.job1.results_location.replace(".apk.raw",".apk.xml.flowdroid.result.instrumentation")
            job2 = x.job2.results_location.replace(".apk.raw",".apk.xml.flowdroid.result.instrumentation")

            split = job1.split("/");

            inst_file_1 = "";
            i=0;
            for st in split:
                if i == 5:
                    inst_file_1+="/xml_scripts"
                inst_file_1+="/"+st;
                i+=1;

            inst_file_1=inst_file_1[1:];

            split=job2.split("/");
            inst_file_2 = "";
            i=0;
            for st in split:
                if i==5:
                    inst_file_2+="/xml_scripts"
                inst_file_2+="/"+st;
                i+=1;
            inst_file_2=inst_file_2[1:]

            lineDiff = self.get_diff_for_files(inst_file_1,inst_file_2,x.partial_orders);
            rList.append(LocalizeResult(str(lineDiff),str(target),x.partial_orders))
        return rList;
