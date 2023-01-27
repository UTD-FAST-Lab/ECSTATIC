#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


import importlib
import logging
import os
import subprocess
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Dict, Tuple

from src.ecstatic.models.Level import Level
from src.ecstatic.models.Option import Option
from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util import FuzzingJob
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob, BenchmarkRecord

logger = logging.getLogger(__name__)

def create_shell_file(job: FuzzingJob, output_folder: str) -> str:
    """Create a shell script file with the configuration the fuzzer is generating."""
    config_str = FlowDroidRunner.dict_to_config_str(job.configuration)
    hash_value = AbstractCommandLineToolRunner.dict_hash(job.configuration)
    shell_file_dir = os.path.join(output_folder, "shell_files")
    Path(shell_file_dir).mkdir(exist_ok=True)

    shell_file_name = os.path.join(shell_file_dir,
                                   f"{hash_value}.sh")
    if not os.path.exists(shell_file_name):
        logger.debug(f'Creating shell file {shell_file_name}')
        with importlib.resources.as_file(
                importlib.resources.files("src.resources.tools.flowdroid").joinpath("flowdroid.sh")) as shell_file,\
                open(shell_file, 'r') as infile:
            content = infile.readlines()

        content = map(lambda r: r.replace('%CONFIG%', config_str), content)
        content = map(lambda r: r.replace('%FLOWDROID_HOME%', "/FlowDroid"), content)
        content = map(lambda r: r.replace('%SOURCE_SINK_LOCATION%',
                                          "/FlowDroid/soot-infoflow-android/SourcesAndSinks.txt"),
                      content)

        with open(shell_file_name, 'w') as f:
            f.writelines(content)

        os.chmod(shell_file_name, 0o777)
    else:
        logger.debug(f'{os.path.basename(shell_file_name)} already exists. Returning.')
    return shell_file_name


def category_and_apk(path: str) -> str:
    return f'{os.path.basename(os.path.dirname(path))}_{os.path.basename(path)}'


def create_xml_config_file(shell_file_path: str, apk: BenchmarkRecord, output_folder: str) -> str:
    """Fill out the template file with information from ecstatic's config."""
    xml_output_folder = os.path.join(output_folder, "xml_scripts")
    Path(xml_output_folder).mkdir(exist_ok=True)
    prefix = os.path.basename(shell_file_path).replace('.sh', '')
    xml_output_file = os.path.join(xml_output_folder,
                                   f"{prefix + '_' + os.path.basename(apk.name)}.xml")
    flowdroid_output = os.path.abspath(xml_output_file) + ".flowdroid.result"
    # if verify:
    #     xml_output_file += '.verify'
    #     flowdroid_output += '.verify'
    if not os.path.exists(xml_output_file):
        logger.info(f'Creating {xml_output_file}')
        with importlib.resources.as_file(importlib.resources.files("src.resources.tools.flowdroid").joinpath("template.xml")) as template:
            aql_config = ElementTree.parse(template)
            for element in aql_config.iter():
                if element.tag == 'path':
                    element.text = os.path.abspath("/FlowDroid")
                elif element.tag == 'run':
                    element.text = f"{os.path.abspath(shell_file_path)} %MEMORY% %APP_APK% %ANDROID_PLATFORMS% " + \
                                   flowdroid_output
                elif element.tag == 'runOnExit':
                    with importlib.resources.as_file(importlib.resources.files("src.resources.tools.flowdroid").joinpath("flushMemory.sh")) as flushMemory:
                        element.text = os.path.abspath(flushMemory)
                elif element.tag == 'runOnAbort':
                    with importlib.resources.as_file(importlib.resources.files('src.resources.tools.flowdroid').joinpath('killpid.sh')) as killPid:
                        element.text = f"{os.path.abspath(killPid)} %PID%"
                elif element.tag == 'result':
                    element.text = flowdroid_output
                elif element.tag == 'androidPlatforms':
                    element.text = "/lib/android-sdk/platforms"

            aql_config.write(xml_output_file)
    else:
        logger.info(f'AQL config file {xml_output_file} already exists. Returning')
    return xml_output_file


class FlowDroidRunner(AbstractCommandLineToolRunner):

    @staticmethod
    def dict_to_config_str(config_as_dict: Dict[Option, Level]) -> str:
        """Transforms a dictionary to a config string"""
        result = ""
        for k, v in config_as_dict.items():
            k: Option
            v: Level
            if k.name == 'taintwrapper' and v.level_name == 'EASY':  # taintwrapper EASY requires an option
                result += f'--taintwrapper EASY -t /FlowDroid/soot-infoflow/EasyTaintWrapperSource.txt'
            elif isinstance(v.level_name, int) or \
                    v.level_name.lower() not in ['false', 'true', 'default', k.get_default().level_name.lower()]:
                result += f'--{k.name} {v.level_name} '
            elif v.level_name.lower() == 'true':
                result += f'--{k.name} '
        return result

    def try_run_job(self, job: FuzzingJob, output_folder: str) -> Tuple[str, str]:
        result_location: str
        shell_location: str = create_shell_file(job, output_folder)
        xml_location: str = create_xml_config_file(shell_location, job.target, output_folder)
        logger.info(f'Running job with configuration {xml_location} on apk {job.target.name}')
        result_location, output = self.run_aql(job, self.get_output(output_folder, job), xml_location)
        logger.info(f'Job on configuration {xml_location} on apk {job.target} done.')
        return result_location, output


    def run_aql(self,
                job: FuzzingJob,
                output: str,
                xml_config_file: str) -> Tuple[str, str]:
        """
        Runs Flowdroid given a config.
        The steps to running flowdroid are:
        1) Modifying the shell script that AQL's config file uses.
        2) Run AQL, save output somewhere.
        """
        # create output file
        try:
            with importlib.resources.as_file(importlib.resources.files("src.resources.tools.flowdroid").joinpath("run_aql.sh")) as run_aql:
                cmd = [os.path.abspath(run_aql),
                       os.path.abspath(xml_config_file),
                       os.path.abspath(job.target.name), output]
                if self.timeout is not None:
                    cmd.append(str(self.timeout))
                curdir = os.path.abspath(os.curdir)
                os.chdir("/AQL-System/target/build")
                logger.info(f'Cmd is {" ".join(cmd)}')
                cp = subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
                if 'FlowDroid successfully executed' not in cp.stdout:
                    raise RuntimeError(cp.stdout)
                os.chdir(curdir)
                if not os.path.exists(output):
                    answers = ElementTree.Element('answer')
                    tree = ElementTree.ElementTree(answers)
                    tree.write(output)
                return output, cp.stdout

        except KeyboardInterrupt:
            if os.path.exists(output):
                os.remove(output)
            return None
