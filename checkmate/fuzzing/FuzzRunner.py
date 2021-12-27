import logging
import os
import subprocess
import sys
import time
from typing import List, Dict
import xml.etree.ElementTree as ET

from checkmate.fuzzing.FuzzLogger import FuzzLogger
from checkmate.models.Flow import Flow
from checkmate.util import FuzzingPairJob, config

class FuzzRunner:
    
    def __init__(self, apk_location: str, fuzzlogger: FuzzLogger):
        self.fuzzlogger = fuzzlogger
        self.apk_location = apk_location
        
    def runJob(self, job: FuzzingPairJob) -> str:
        logging.debug(f'Running job: {job}')
        for a in self.get_apks(self.apk_location):
            classified = list()
            locations = list()
            for c in [job.config1, job.config2]:
                if self.fuzzlogger.checkIfHasBeenRun(c, a):
                    logging.info(f'Configuration {c} on apk {a} has already been run. Skipping')
                    continue
                c_str = self.dict_to_config_str(c)
                shell_location = self.create_shell_file(c_str)
                xml_location = self.create_xml_config_file(shell_location)
                results_location = self.run_aql(a, xml_location)
                locations.append(results_location)
                classified.append(self.num_tp_fp_fn(results_location, a))
                os.remove(shell_location)
                os.remove(xml_location)
                self.fuzzlogger.logNewConfig(c, a)

            if job.soundness_level == -1:  # -1 means that the job.config1 is as sound as job.config2
                violated = classified[1]['tp'] > classified[0]['tp']
            elif job.soundness_level == 1:  # 1 means that job.config2 is as sound as job.config1
                violated = classified[0]['tp'] > classified[1]['tp']
            if violated:
                result = f'VIOLATION: {job.option_under_investigation} on {a} ({job.config1};{classified[0]} ' \
                         f'{"more sound than" if job.soundness_level == -1 else "less sound than"} {job.config2};{classified[1]}) ' \
                         f'(files are {results_location})'
            else:
                result = f'SUCCESS: {job.option_under_investigation} on {a} ({job.config1};{classified[0]} ' \
                         f'{"more sound than" if job.soundness_level == -1 else "less sound than"} {job.config2};{classified[1]}) ' \
                         f'(files are {results_location})'
            return result

    def num_tp_fp_fn(self, output_file: str, apk_name: str) -> Dict[str, int]:
        """
        Given an output file and the apk name, check the ground truth file.
        """
        try:
            output_flows = [Flow(f) for f in ET.parse(output_file).getroot().find('flows').findall('flow')]
        except AttributeError:
            output_flows = []
        gt_flows = list(
            filter(
                lambda f: os.path.basename(apk_name) == os.path.basename(f.get_file()),
                [Flow(f) for f in
                 ET.parse(config.configuration['ground_truth_location']).getroot().findall('flow')]
            )
        )
        logging.info(f'output flows is {len(output_flows)} flows long.')
        logging.info(f'gt flows is {len(gt_flows)} flows long.')
        tp = filter(lambda f: f.get_classification(), gt_flows)
        fp = filter(lambda f: not f.get_classification(), gt_flows)
        result = dict()
        result['tp'] = len(list(filter(lambda f: f in output_flows, tp)))
        result['fp'] = len(list(filter(lambda f: f in output_flows, fp)))
        result['fn'] = len(list(filter(lambda f: f not in output_flows, tp)))
        return result

    def dict_to_config_str(self, config_as_dict: Dict[str, str]) -> str:
        """Transforms a dictionary to a config string"""
        result = ""
        for k, v in config_as_dict.items():
            if v.lower() not in ['false', 'true', 'default']:
                result += f'--{k} {v} '
            elif v.lower() == 'true':
                result += f'--{k} '
        return result

    def create_shell_file(self, config_str: str) -> str:
        """Create a shell script file with the configuration the fuzzer is generating."""
        with open(config.configuration['shell_template_location'], 'r') as infile:
            content = infile.readlines()

        content = map(lambda r: r.replace('%CONFIG%', config_str), content)
        content = map(lambda r: r.replace('%FLOWDROID_HOME%', config.configuration['flowdroid_root']), content)
        content = map(lambda r: r.replace('%SOURCE_SINK_LOCATION%', config.configuration['source_sink_location']),
                      content)

        shell_file_name = os.path.join(config.configuration['output_directory'],
                                       f"{str(time.time())}.sh")

        with open(shell_file_name, 'w') as f:
            f.writelines(content)

        os.chmod(shell_file_name, 0o777)
        return shell_file_name

    def create_xml_config_file(self, shell_file_path: str) -> str:
        """Fill out the template file with information from checkmate's config."""
        prefix = os.path.basename(shell_file_path).replace('.sh', '')

        aql_config = ET.parse(config.configuration['aql_template_location'])
        for element in aql_config.iter():
            if element.tag == 'path':
                element.text = os.path.abspath(config.configuration["flowdroid_root"])
            elif element.tag == 'run':
                element.text = f"{os.path.abspath(shell_file_path)} %MEMORY% %APP_APK% %ANDROID_PLATFORMS% " + \
                               os.path.abspath(
                                   f"{os.path.join(config.configuration['output_directory'], prefix + '_flowdroid.result')}")
            elif element.tag == 'runOnExit':
                element.text = os.path.abspath(config.configuration['flushmemory_location'])
            elif element.tag == 'runOnAbort':
                element.text = os.path.abspath(f"{config.configuration['killpid_location']} %PID%")
            elif element.tag == 'result':
                element.text = os.path.abspath(
                    os.path.join(config.configuration['output_directory'], prefix + '_flowdroid.result'))
            elif element.tag == 'androidPlatforms':
                element.text = os.path.abspath(config.configuration['android_platforms_location'])

        output_file = os.path.join(config.configuration['output_directory'], f"{os.path.join(prefix)}.xml")
        aql_config.write(output_file)
        return output_file

    def run_aql(self, apk: str,
                xml_config_file: str) -> str:
        """
        Runs Flowdroid given a config.
        The steps to running flowdroid are:
        1) Modifying the shell script that AQL's config file uses.
        2) Run AQL, save output somewhere.
        """
        # create output file
        b = os.path.basename(xml_config_file)
        output = os.path.join(config.configuration['output_directory'],
                              os.path.basename(apk) + \
                              os.path.basename(xml_config_file))
        output = os.path.abspath(output)
        # check if it exists
        if not os.path.exists(output):
            cmd = [config.configuration['aql_run_script_location'], os.path.abspath(xml_config_file),
                   os.path.abspath(apk), output]
            curdir = os.path.abspath(os.curdir)
            os.chdir(os.path.dirname(config.configuration['aql_location']))
            loop = True
            while loop:
                start = time.time()
                logging.info(f'Cmd is {cmd}')
                cp = subprocess.run(cmd, capture_output=True)
                t = time.time() - start
                loop = False if (b'FlowDroid successfully executed' in cp.stdout) else True
            os.chdir(curdir)
            if os.path.exists(output):
                tree = ET.parse(output)
                root = tree.getroot()
                root.set("time", str(t))
            else:
                answers = ET.Element('answer')
                answers.set('time', str(t))
                tree = ET.ElementTree(answers)

            tree.write(output)
        return output

    def get_apks(self, directory: str) -> List[str]:
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith('.apk'):
                    yield os.path.join(root, f)
