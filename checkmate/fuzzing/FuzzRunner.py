import logging
import os
import subprocess
import time
import copy
import xml.etree.ElementTree as ElementTree
from typing import List, Dict, Union

from checkmate.fuzzing.FuzzLogger import FuzzLogger
from checkmate.models.Flow import Flow
from checkmate.util import FuzzingPairJob, config

RUN_THRESHOLD = 5  # how many times to try to reattempt running AQL
logger = logging.getLogger(__name__)


def run_aql(apk: str,
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
                          os.path.basename(apk) +
                          os.path.basename(xml_config_file))
    output = os.path.abspath(output)
    # check if it exists
    if os.path.exists(output):
        os.remove(output)

    cmd = [config.configuration['aql_run_script_location'], os.path.abspath(xml_config_file),
           os.path.abspath(apk), output]
    curdir = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(config.configuration['aql_location']))
    num_runs = 0
    while num_runs < RUN_THRESHOLD:
        start = time.time()
        logger.info(f'Cmd is {cmd}')
        cp = subprocess.run(cmd, capture_output=True)
        t = time.time() - start
        if b'FlowDroid successfully executed' in cp.stdout:
            break
        num_runs += 1
    if num_runs == RUN_THRESHOLD:
        raise RuntimeError(f'Could not run configuration specified in file {xml_config_file} on {apk}. '
                           f'Tried to run {RUN_THRESHOLD} times but it failed each time.')
    os.chdir(curdir)
    if os.path.exists(output):
        tree = ElementTree.parse(output)
        root = tree.getroot()
        root.set("time", str(t))
    else:
        answers = ElementTree.Element('answer')
        answers.set('time', str(t))
        tree = ElementTree.ElementTree(answers)

    tree.write(output)
    return output


def create_xml_config_file(shell_file_path: str) -> str:
    """Fill out the template file with information from checkmate's config."""
    prefix = os.path.basename(shell_file_path).replace('.sh', '')
    output_file = os.path.join(config.configuration['output_directory'], f"{os.path.join(prefix)}.xml")
    if not os.path.exists(output_file):
        aql_config = ElementTree.parse(config.configuration['aql_template_location'])
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

        aql_config.write(output_file)
    return output_file


def create_shell_file(config_str: str) -> str:
    """Create a shell script file with the configuration the fuzzer is generating."""

    shell_file_name = os.path.join(config.configuration['output_directory'],
                                   f"{hash(config_str)}.sh")
    if not os.path.exists(shell_file_name):
        with open(config.configuration['shell_template_location'], 'r') as infile:
            content = infile.readlines()

        content = map(lambda r: r.replace('%CONFIG%', config_str), content)
        content = map(lambda r: r.replace('%FLOWDROID_HOME%', config.configuration['flowdroid_root']), content)
        content = map(lambda r: r.replace('%SOURCE_SINK_LOCATION%', config.configuration['source_sink_location']),
                      content)

        with open(shell_file_name, 'w') as f:
            f.writelines(content)

        os.chmod(shell_file_name, 0o777)

    return shell_file_name


def dict_to_config_str(config_as_dict: Dict[str, str]) -> str:
    """Transforms a dictionary to a config string"""
    result = ""
    for k, v in config_as_dict.items():
        if v.lower() not in ['false', 'true', 'default']:
            result += f'--{k} {v} '
        elif v.lower() == 'true':
            result += f'--{k} '
    return result


def num_tp_fp_fn(output_file: str, apk_name: str) -> Dict[str, int]:
    """
    Given an output file and the apk name, check the ground truth file.
    """
    try:
        output_flows = [Flow(f) for f in ElementTree.parse(output_file).getroot().find('flows').findall('flow')]
    except AttributeError:
        output_flows = []
    gt_flows = list(
        filter(
            lambda f: os.path.basename(apk_name) == os.path.basename(f.get_file()),
            [Flow(f) for f in
             ElementTree.parse(config.configuration['ground_truth_location']).getroot().findall('flow')]
        )
    )
    logger.info(f'output flows is {len(output_flows)} flows long.')
    logger.info(f'gt flows is {len(gt_flows)} flows long.')
    tp = filter(lambda f: f.get_classification(), gt_flows)
    fp = filter(lambda f: not f.get_classification(), gt_flows)
    result = dict()
    result['tp'] = (set(filter(lambda f: f in output_flows, tp)))
    result['fp'] = (set(filter(lambda f: f in output_flows, fp)))
    result['fn'] = (set(filter(lambda f: f not in output_flows, tp)))
    return result


class FuzzRunner:

    def __init__(self, apk_location: str, fuzzlogger: FuzzLogger):
        self.fuzzlogger = fuzzlogger
        self.apk_location = apk_location

    def run_job(self, job: FuzzingPairJob) -> Dict[str, Union[str, float]]:
        logger.debug(f'Running job: {job}')
        results = list()
        classified = list()
        start_time = time.time()
        if self.fuzzlogger.check_if_has_been_run(job.config1, job.apk) and \
                self.fuzzlogger.check_if_has_been_run(job.config2, job.apk):
            logger.warning(f'Configurations {job.config1},{job.config2} on apk '
                           f'{job.apk} has already been run. Skipping')
            return None
        try:
            for c in [job.config1, job.config2]:
                c_str = dict_to_config_str(c)
                shell_location = create_shell_file(c_str)
                xml_location = create_xml_config_file(shell_location)
                results_location = run_aql(job.apk, xml_location)
                classified.append(num_tp_fp_fn(results_location, job.apk))
        except RuntimeError as re:
            logger.exception("Failed to run pair. Skipping to next pair.")
            return None

        end_time = time.time()

        if job.soundness_level == -1:  # -1 means that the job.config1 is as sound as job.config2
            violated = len(classified[1]['tp'] - classified[0]['tp']) > 0
        elif job.soundness_level == 1:  # 1 means that job.config2 is as sound as job.config1
            violated = len(classified[0]['tp'] - classified[1]['tp']) > 0

        root = ElementTree.Element('flowset')
        root.set('config1', job.config1)
        root.set('config2', job.config2)
        root.set('type', 'soundness')
        root.set('violation', str(violated))

        if violated:
            preserve_set_1 = classified[0]['tp'] - classified[1]['tp'] if job.soundness_level == 1 else set()
            preserve_set_2 = classified[1]['tp'] - classified[0]['tp'] if job.soundness_level == -1 else set()
        else:
            preserve_set_1 = classified[0]['tp']
            preserve_set_2 = classified[1]['tp']

        for j, c in [(job.config1, preserve_set_1), (job.config2, preserve_set_2)]:
            preserve = ElementTree.Element('preserve')
            preserve.set('config', j)
            for f in c:
                f: Flow
                preserve.append(f.element)
            root.append(preserve)

        tree = ElementTree.ElementTree(root)
        output_dir = os.path.join(config.configuration['output_directory'],
                                  f"{hash(dict_to_config_str(job.config1))}_{hash(dict_to_config_str(job.config2))}")

        try:
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
        except FileExistsError as fe:
            pass # silently ignore, we don't care

        output_file = os.path.join(output_dir, f'flowset_violation-{violated}_{os.path.basename(job.apk)}.xml')
        tree.write(output_file)

        result = {'type': 'VIOLATION' if violated else 'SUCCESS',
                  'apk': job.apk,
                  'config1': job.config1,
                  'config2': job.config2,
                  'results': output_file,
                  'start_time': start_time,
                  'end_time': end_time,
                  'relation': "more sound than" if job.soundness_level == -1 else "less sound than",
                  'option_under_investigation': job.option_under_investigation,
                  'classification_1': list(classified[0]),
                  'classification_2': list(classified[1])
                  }

        return result
