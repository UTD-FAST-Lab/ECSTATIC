import sys
import os
import json
import logging
from src.ecstatic.localization import AbstractLocalization;
from src.ecstatic.localization import LocalizeResult;

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
    def get_diff_for_files(self,file1,file2):
        f1_lines = []
        f2_lines = []
        with open(file1,'r') as fp:
            f1_lines = fp.readlines()
        with open(file2,'r') as fp:
            f2_lines = fp.readlines()

        f1_dict = get_dict_for_file(f1_lines)
        f2_dict = get_dict_for_file(f2_lines)

        f1_lines = [*f1_dict]
        f2_lines = [*f2_dict]

        lineDiff=0
        # 1 -> 2, A -> B
        for x in f2_lines:
            if x not in f1_lines:
                lineDiff+=1;

        return lineDiff;


    def localize(self):
        #Internal logic for running this localizer
        logging.warning("Started Localize")
        #go through all violations and check em out
        rList: List[LocalizeResult] = []
        for x in self.violations:
            jsonObj = json.loads(json.dumps(x.as_dict()));

            #we are interested in a couple things, mostly
            # the apk
            # the two files that contain instrumentation info
            # the partial_orders being bad
            target = jsonObj["target"];
            target = target[target.rindex("/")+1:];

            job1 = jsonObj["job1"]["result"].replace(".apk.raw",".apk.xml.flowdroid.result.instrumentation")
            job2 = jsonObj["job2"]["result"].replace(".apk.raw",".apk.xml.flowdroid.result.instrumentation")

            split = job1.split("/");

            inst_file_1 = "";
            i=0;
            for st in split:
                if i == 4:
                    inst_file_1+="/xml_scripts"
                inst_file_1+="/"+st;
                i+=1;

            inst_file_1=inst_file_1[1:];

            split=job2.split("/");
            inst_file_2 = "";
            i=0;
            for st in split:
                if i==4:
                    inst_file_2+="/xml_scripts"
                inst_file_2+="/"+st;
                i+=1;
            inst_file_2=inst_file_2[1:]

            lineDiff = get_diff_for_files(inst_file_1,inst_file_2);
            rList.append(LocalizeResult(str(lineDiff),str(target),str(jsonObj["partial_orders"][0])))
        return rList;
