# Class that reverts a tool to the correct version


# Grab commits
from abc import ABC
from pydriller import Repository, Git
import xml.etree.ElementTree as ET
import os
import subprocess


class ReverterFactory:
    @staticmethod
    def get_reverter(tool_name, from_tag, to_tag):
        if tool_name == "wala":
            return WalaReverter(from_tag, to_tag);
        else:
            print("Reverter not supported")
            exit(-1);


class Reverter(ABC):

    def revert_tool(self, git_repo: Repository, commit: str):
        pass;


class WalaReverter(Reverter):

    def __init__(self, from_tag, to_tag):
        self.FILE_PATH = "/WALAInterface/";
        self.GITREPO = "/binary_search_project/WALA"
        self.FROM_TAG = from_tag;
        self.TO_TAG = to_tag;
        ET.register_namespace('', 'http://maven.apache.org/POM/4.0.0')

    # this will take in some information about the tool (wala in this case) and change WALAInterface to support the new version of wala
    def revert_tool(self, git_repo: Repository, commit: str) -> bool:
        # change tools
        Git("/binary_search_project/WALA/").checkout(commit);
        interface_pom = ET.parse("/WALAInterface/pom.xml")
        wala_pom = ET.parse("/binary_search_project/WALA/pom.xml");

        interface_xml = interface_pom.getroot()
        wala_xml = wala_pom.getroot();

        # text to change the WALAInterface version of WALA to
        new_version_text = wala_xml[3].text;

        interface_xml[5][0][2].text = new_version_text;
        interface_xml[5][1][2].text = new_version_text;
        interface_pom.write(file_or_filename=self.FILE_PATH + "pom.xml", encoding='utf-8');

        # build them both
        cdir = os.getcwd();
        try:
            command_run = self.GITREPO+"/gradlew"+" clean publishToMavenLocal -x test -x javadoc -x testClasses -x " \
                                                  "testFixturesJavadoc -p C:/binary_search_project/WALA/ "
            output = subprocess.check_output(command_run, shell=True);
            command_run2 = "mvn clean package"

            os.chdir(self.FILE_PATH);
            output2 = subprocess.check_output(command_run2, shell=True);
            os.chdir(cdir)
            return True;
        except subprocess.CalledProcessError:
            os.chdir(cdir)
            return False;
