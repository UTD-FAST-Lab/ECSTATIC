import logging
import os
import subprocess
import time
import xml.etree.ElementTree as ElementTree
from typing import Dict, Set

from src.checkmate.models.Flow import Flow
from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.util import FuzzingJob, config
from src.checkmate.util.UtilClasses import FlowdroidFinishedFuzzingJob

RUN_THRESHOLD = 2  # how many times to try to reattempt running AQL
logger = logging.getLogger(__name__)


def run_aql(apk: str,
            xml_config_file: str,
            verify: bool) -> str:
    """
    Runs Flowdroid given a config.
    The steps to running flowdroid are:
    1) Modifying the shell script that AQL's config file uses.
    2) Run AQL, save output somewhere.
    """
    try:
        # create output file
        output = os.path.abspath(xml_config_file) + '.aql.result'
        if verify:
            output += '.verify'

        if os.path.exists(output):
            print(f'Found result already for config {xml_config_file} on {apk}')
            return output

        if os.path.exists(output + '.timedout'):
            raise TimeoutError(f'Skipping run for {xml_config_file} on {apk} because it timed out last time.')

        cmd = [config.configuration['aql_run_script_location'], os.path.abspath(xml_config_file),
               os.path.abspath(apk), output]
        curdir = os.path.abspath(os.curdir)
        os.chdir(os.path.dirname(config.configuration['aql_location']))
        num_runs = 0
        while num_runs < RUN_THRESHOLD:
            start = time.time()
            logger.info(f'Cmd is {" ".join(cmd)}')
            cp = subprocess.run(cmd, capture_output=True)
            t = time.time() - start
            if b'FlowDroid successfully executed' in cp.stdout:
                break
            print(f'Restarting {xml_config_file} on {apk}, since it failed.')
            num_runs += 1
        if num_runs == RUN_THRESHOLD:
            if os.path.exists(output):
                os.remove(output)
            with open(output + '.timedout', 'w'):
                pass
            raise TimeoutError(f'Could not run configuration specified in file {xml_config_file} on {apk}. '
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

    except KeyboardInterrupt as ki:
        if os.path.exists(output):
            os.remove(output)
        return None


def create_xml_config_file(shell_file_path: str, apk: str, verify: bool) -> FlowdroidFinishedFuzzingJob:
    """Fill out the template file with information from checkmate's config."""
    prefix = os.path.basename(shell_file_path).replace('.sh', '')
    xml_output_file = os.path.join(config.configuration['output_directory'],
                                   f"{prefix + '_' + category_and_apk(apk).replace('/', '_')}.xml")
    flowdroid_output = os.path.abspath(xml_output_file) + ".flowdroid.result"
    if verify:
        xml_output_file += '.verify'
        flowdroid_output += '.verify'
    if not os.path.exists(xml_output_file):
        logger.info(f'Creating {xml_output_file}')
        aql_config = ElementTree.parse(config.configuration['aql_template_location'])
        for element in aql_config.iter():
            if element.tag == 'path':
                element.text = os.path.abspath(config.configuration["flowdroid_root"])
            elif element.tag == 'run':
                element.text = f"{os.path.abspath(shell_file_path)} %MEMORY% %APP_APK% %ANDROID_PLATFORMS% " + \
                               flowdroid_output
            elif element.tag == 'runOnExit':
                element.text = os.path.abspath(config.configuration['flushmemory_location'])
            elif element.tag == 'runOnAbort':
                element.text = os.path.abspath(f"{config.configuration['killpid_location']} %PID%")
            elif element.tag == 'result':
                element.text = flowdroid_output
            elif element.tag == 'androidPlatforms':
                element.text = os.path.abspath(config.configuration['android_platforms_location'])

        aql_config.write(xml_output_file)
    else:
        logger.info(f'AQL config file {xml_output_file} already exists. Returning')
    return xml_output_file


def create_shell_file(configuration: Dict[Option, Level]) -> str:
    """Create a shell script file with the configuration the fuzzer is generating."""
    config_str = FlowdroidRunnerAbstract.dict_to_config_str(configuration)
    hash_value = AbstractCommandLineToolRunner.dict_hash(configuration)
    shell_file_name = os.path.join(config.configuration['output_directory'],
                                   f"{hash_value}.sh")
    if not os.path.exists(shell_file_name):
        logger.debug(f'Creating shell file {shell_file_name}')
        with open(config.configuration['shell_template_location'], 'r') as infile:
            content = infile.readlines()

        content = map(lambda r: r.replace('%CONFIG%', config_str), content)
        content = map(lambda r: r.replace('%FLOWDROID_HOME%', config.configuration['flowdroid_root']), content)
        content = map(lambda r: r.replace('%SOURCE_SINK_LOCATION%', config.configuration['source_sink_location']),
                      content)

        with open(shell_file_name, 'w') as f:
            f.writelines(content)

        os.chmod(shell_file_name, 0o777)
    else:
        logger.debug(f'{os.path.basename(shell_file_name)} already exists. Returning.')
    return shell_file_name


def category_and_apk(path: str) -> str:
    return f'{os.path.basename(os.path.dirname(path))}/{os.path.basename(path)}'


def num_tp_fp_fn(output_file: str, apk_name: str) -> Dict[str, Set[Flow]]:
    """
    Given an output file and the apk name, check the ground truth file.
    """
    try:
        output_flows = [Flow(f) for f in ElementTree.parse(output_file).getroot().find('flows').findall('flow')]
    except AttributeError:
        output_flows = []

    logging.warning("Made a change for DroidBench -- make sure to revert if you need to do FossDroid!")
    gt_flows = list(
        filter(
            lambda f: category_and_apk(apk_name) == category_and_apk(f.get_full_file()),
            [Flow(f) for f in
             ElementTree.parse(config.configuration['ground_truth_location']).getroot().findall('flow')]
        )
    )
    tp = [f for f in gt_flows if f.get_classification() == 'TRUE']
    fp = [f for f in gt_flows if f.get_classification() == 'FALSE']
    print(f'{len(tp)} true positives and {len(fp)} false positives for this apk.')
    if len(set(fp)) > 0:
        logger.info(f'Found {len(set(fp))} false positives in {gt_flows}')
    result = dict()
    result['tp'] = (set(filter(lambda f: f in tp, output_flows)))
    result['fp'] = (set(filter(lambda f: f in fp, output_flows)))
    result['fn'] = (set(filter(lambda f: f not in tp, output_flows)))
    print(f'Found {len(result["tp"])} true positives.')
    print(f'Found {len(result["fp"])} false positives.')
    return result


class FlowdroidRunnerAbstract(AbstractCommandLineToolRunner):

    @staticmethod
    def dict_to_config_str(config_as_dict: Dict[Option, Level]) -> str:
        """Transforms a dictionary to a config string"""
        result = ""
        for k, v in config_as_dict.items():
            k: Option
            v: Level
            if k.name == 'taintwrapper' and v.level_name == 'EASY':  # taintwrapper EASY requires an option
                result += f'--taintwrapper EASY -t {config.configuration["taintwrapper_easy_location"]} '
            elif v.level_name.lower() not in ['false', 'true', 'default', k.get_default().lower()]:
                result += f'--{k.name} {v.level_name} '
            elif v.level_name.lower() == 'true':
                result += f'--{k.name} '
        return result

    def run_job(self, job: FuzzingJob, verify: bool = False) -> FlowdroidFinishedFuzzingJob:
        try:
            start_time: float = time.time()
            result_location: str
            shell_location: str = create_shell_file(job.configuration)
            xml_location: str = create_xml_config_file(shell_location, job.apk, verify)
            print(f'Running job with configuration {xml_location} on apk {job.apk}')
            result_location = run_aql(job.apk, xml_location, verify)
            print(f'Job on configuration {xml_location} on apk {job.apk} done.')
            classified: Dict[str, Set[Flow]] = num_tp_fp_fn(result_location, job.apk)

            end_time: float = time.time()

            return FlowdroidFinishedFuzzingJob(
                job=job,
                execution_time=(end_time - start_time),
                results_location=result_location,
                configuration_location=xml_location,
                detected_flows=classified)
        except (KeyboardInterrupt, TimeoutError, RuntimeError) as ex:
            #logger.exception(f'Failed to run configuration {xml_location} on apk {job.apk}')
            return None