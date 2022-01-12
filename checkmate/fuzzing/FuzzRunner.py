import hashlib
import logging
import os
import subprocess
import time
import xml.etree.ElementTree as ElementTree
from typing import Dict, Union, Set

from frozendict import frozendict

from checkmate.models.Flow import Flow
from checkmate.models.Level import Level
from checkmate.models.Option import Option
from checkmate.util import FuzzingJob, config
from checkmate.util.NamedTuples import FinishedFuzzingJob

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
    try:
        # create output file
        output = os.path.join(config.configuration['output_directory'],
                              os.path.basename(apk) +
                              os.path.basename(xml_config_file))
        output = os.path.abspath(output)

        if os.path.exists(output):
            logger.info(f'Found result already for config {xml_config_file} on {apk}')
            return output

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

    except KeyboardInterrupt as ki:
        if os.path.exists(output):
            os.remove(output)
        return None




def create_xml_config_file(shell_file_path: str) -> str:
    """Fill out the template file with information from checkmate's config."""
    prefix = os.path.basename(shell_file_path).replace('.sh', '')
    output_file = os.path.join(config.configuration['output_directory'], f"{os.path.join(prefix)}.xml")
    if not os.path.exists(output_file):
        logger.info(f'Creating {output_file}')
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
    else:
        logger.info(f'AQL config file {output_file} already exists. Returning')
    return output_file


def create_shell_file(configuration: Dict[Option, Level]) -> str:
    """Create a shell script file with the configuration the fuzzer is generating."""
    hash_value = hashlib.md5()
    config_as_string = str(sorted({str(k): str(v) for k, v in configuration.items()}.items(), key=lambda x: x[0]))
    hash_value.update(config_as_string.encode('utf-8'))
    shell_file_name = os.path.join(config.configuration['output_directory'],
                                   f"{hash_value.hexdigest()}.sh")
    config_str = dict_to_config_str(configuration)
    logger.info(f'Hashed configuration {config_as_string} to {os.path.basename(shell_file_name)}')
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


def dict_to_config_str(config_as_dict: Dict[Option, Level]) -> str:
    """Transforms a dictionary to a config string"""
    result = ""
    for k, v in config_as_dict.items():
        if v.level_name.lower() not in ['false', 'true', 'default']:
            result += f'--{k.name} {v.level_name} '
        elif v.level_name.lower() == 'true':
            result += f'--{k.name} '
    return result


def num_tp_fp_fn(output_file: str, apk_name: str) -> Dict[str, Set[Flow]]:
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
    tp = filter(lambda f: f.get_classification(), gt_flows)
    fp = filter(lambda f: not f.get_classification(), gt_flows)
    result = dict()
    result['tp'] = (set(filter(lambda f: f in output_flows, tp)))
    result['fp'] = (set(filter(lambda f: f in output_flows, fp)))
    result['fn'] = (set(filter(lambda f: f not in output_flows, tp)))
    return result


class FuzzRunner:

    def __init__(self, apk_location: str):
        self.apk_location = apk_location

    def run_job(self, job: FuzzingJob) -> Dict[str, Union[str, float]]:
        logger.debug(f'Running job with configuration {str(job.configuration)} on apk {job.apk}')
        start_time: float = time.time()
        result_location: str
        try:
            shell_location: str = create_shell_file(job.configuration)
            xml_location: str = create_xml_config_file(shell_location)
            result_location = run_aql(job.apk, xml_location)
            classified: Dict[str, Set[Flow]] = num_tp_fp_fn(result_location, job.apk)

            end_time: float = time.time()

            return FinishedFuzzingJob(
                job=job,
                execution_time=(end_time - start_time),
                results_location=result_location,
                configuration_location=xml_location,
                detected_flows=classified)
        except (KeyboardInterrupt, RuntimeError) as ex:
            logger.exception("Failed to run. Cleaning up gracefully.")
            if result_location is not None:
                os.remove(result_location)
            return None

        #
        # if job.soundness_level == -1:  # -1 means that the job.config1 is as sound as job.config2
        #     # thus, violation if job.config2 produced true positives that job.config1 did not.
        #     violated = len(classified[1]['tp'] - classified[0]['tp']) > 0
        # elif job.soundness_level == 1:  # 1 means that job.config2 is as sound as job.config1
        #     # thus, violation if job.config1 produced true positives that job.config2 did not.
        #     violated = len(classified[0]['tp'] - classified[1]['tp']) > 0
        #
        # root = ElementTree.Element('flowset')
        # root.set('config1', job.config1)
        # root.set('config2', job.config2)
        # root.set('type', 'soundness')
        # root.set('partial_order',
        #          f'{job.option_under_investigation[0]}={job.config1[job.option_under_investigation[0]]} '
        #          f'{"more sound than" if job.soundness_level < 0 else "less sound than"} '
        #          f'{job.option_under_investigation[0]}={job.config2[job.option_under_investigation[0]]}')
        # root.set('violation', str(violated))
        #
        # if violated:
        #     # we want to only keep the differences (i.e., same computation as violated above)
        #     preserve_set_1 = classified[0]['tp'] - classified[1]['tp'] if job.soundness_level == 1 else set()
        #     preserve_set_2 = classified[1]['tp'] - classified[0]['tp'] if job.soundness_level == -1 else set()
        # else:
        #     preserve_set_1 = classified[0]['tp']
        #     preserve_set_2 = classified[1]['tp']
        #
        # for j, c in [(job.config1, preserve_set_1), (job.config2, preserve_set_2)]:
        #     preserve = ElementTree.Element('preserve')
        #     preserve.set('config', j)
        #     for f in c:
        #         f: Flow
        #         preserve.append(f.element)
        #     root.append(preserve)
        #
        # tree = ElementTree.ElementTree(root)
        # output_dir = os.path.join(config.configuration['output_directory'],
        #                           f"{hash(dict_to_config_str(job.config1))}_{hash(dict_to_config_str(job.config2))}")
        #
        # try:
        #     if not os.path.exists(output_dir):
        #         os.mkdir(output_dir)
        # except FileExistsError as fe:
        #     pass  # silently ignore, we don't care
        #
        # output_file = os.path.join(output_dir, f'flowset_violation-{violated}_{os.path.basename(job.apk)}.xml')
        # tree.write(output_file)
        #
        # result = {'type': 'VIOLATION' if violated else 'SUCCESS',
        #           'apk': job.apk,
        #           'config1': job.config1,
        #           'config2': job.config2,
        #           'results': output_file,
        #           'start_time': start_time,
        #           'end_time': end_time,
        #           'option_under_investigation': job.option_under_investigation,
        #           'classification_1': [(k, len(v)) for k, v in classified[0].items()],
        #           'classification_2': [(k, len(v)) for k, v in classified[1].items()],
        #           'partial_order': f'{job.option_under_investigation[0]}={job.config1[job.option_under_investigation[0]]} '
        #                            f'{"more sound than" if job.soundness_level > 0 else "less sound than"} '
        #                            f'{job.option_under_investigation[0]}={job.config2[job.option_under_investigation[0]]}'
        #           }
        #
        # return result
