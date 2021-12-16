import time
import logging
from checkmate.models.Flow import Flow
from .flowdroid_grammar import FlowdroidGrammar
from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar
from ..models import Option, Tool
from ..util import config
import pickle
import random
import os
import copy
import datetime
import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, List


def main(model_location: str, number_configs: int):
    flowdroid_ebnf_grammar = FlowdroidGrammar.getGrammar()
    flowdroid_grammar = convert_ebnf_grammar(flowdroid_ebnf_grammar)
    fuzzer = GrammarCoverageFuzzer(flowdroid_grammar)
    with open(model_location, 'rb') as f:
        model = pickle.load(f)
    while True:
        fuzzed_config = process_config(fuzzer.fuzz())
        candidates = mutate_config(model, fuzzed_config)
        choice = random.choice(candidates)
        option_under_investigation = [k for k in choice.keys() if k not in fuzzed_config.keys() or fuzzed_config[k] != choice[k]]
        print(f'Pair of configs is {fuzzed_config}, {choice}. Different on {option_under_investigation}.')
        for a in get_apks(config.configuration['apk_location']):
            outputs : List[str] = []
            for c in [fuzzed_config, choice]:
                c_str = dict_to_config_str(c)
                shell_location = create_shell_file(c_str)
                xml_location = create_xml_config_file(shell_location)
                output = run_aql(a, xml_location)
                classified = num_tp_fp_fn(output, a)
                logging.debug(f'Result is {classified}')
                


def num_tp_fp_fn(output_file: str, apk_name: str) -> Dict[str, int]:
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
            [Flow(f) for f in ET.parse(config.configuration['ground_truth_location']).getroot().findall('flow')]
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



def output_file_to_validation_record(output_file: str, option_under_investigation: str) -> Dict[str, str]:
    """
    Reads in an output file and transforms it into the record type
    that the violation checker is expecting.

    Expects the following fields:
    fp: number of false positives
    fn: number of false negatives
    tp: number of true positives
    tn: number of true negatives
    generating_script: the script that generated it
    apk: the number of apks
    """
    return None

def get_apks(directory: str) -> List[str]:
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.apk'):
                yield os.path.join(root, f)

def dict_to_config_str(config_as_dict: Dict[str, str]) -> str:
    """Transforms a dictionary to a config string"""
    result = ""
    for k, v in config_as_dict.items():
        if v.lower() not in ['false', 'true', 'default']:
            result += f'--{k} {v} '
        elif v.lower() == 'true':
            result += f'--{k} '
    return result

def create_shell_file(config_str: str) -> str:
    """Create a shell script file with the configuration the fuzzer is generating."""
    with open(config.configuration['shell_template_location'], 'r') as infile:
        content = infile.readlines()

    content = map(lambda r: r.replace('%CONFIG%', config_str), content)
    content = map(lambda r: r.replace('%FLOWDROID_HOME%', config.configuration['flowdroid_root']), content)
    content = map(lambda r: r.replace('%SOURCE_SINK_LOCATION%', config.configuration['source_sink_location']), content)

    shell_file_name = os.path.join(config.configuration['output_directory'],
                                   f"{str(time.time())}.sh")

    with open(shell_file_name, 'w') as f:
        f.writelines(content)

    os.chmod(shell_file_name, 0o777)
    return shell_file_name

def create_xml_config_file(shell_file_path: str) -> str:
    """Fill out the template file with information from checkmate's config."""
    prefix = os.path.basename(shell_file_path).replace('.sh', '')

    aql_config = ET.parse(config.configuration['aql_template_location'])
    for element in aql_config.iter():
        if element.tag == 'path':
            element.text = os.path.abspath(config.configuration["flowdroid_root"])
        elif element.tag == 'run':
            element.text = f"{os.path.abspath(shell_file_path)} %MEMORY% %APP_APK% %ANDROID_PLATFORMS% " +\
                           os.path.abspath(f"{os.path.join(config.configuration['output_directory'], prefix + '_flowdroid.result')}")
        elif element.tag == 'runOnExit':
            element.text = os.path.abspath(config.configuration['flushmemory_location'])
        elif element.tag == 'runOnAbort':
            element.text = os.path.abspath(f"{config.configuration['killpid_location']} %PID%")
        elif element.tag == 'result':
            element.text = os.path.abspath(os.path.join(config.configuration['output_directory'], prefix + '_flowdroid.result'))
        elif element.tag == 'androidPlatforms':
            element.text = os.path.abspath(config.configuration['android_platforms_location'])

    output_file = os.path.join(config.configuration['output_directory'], f"{os.path.join(prefix)}.xml")
    aql_config.write(output_file)
    return output_file



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
                          os.path.basename(apk) +\
                          os.path.basename(xml_config_file))
    output = os.path.abspath(output)
    # check if it exists
    if not os.path.exists(output):
        cmd = [config.configuration['aql_run_script_location'], os.path.abspath(xml_config_file),
               os.path.abspath(apk), output]
        curdir = os.path.abspath(os.curdir)
        os.chdir(os.path.dirname(config.configuration['aql_location']))
        start = time.time()
        cp = subprocess.run(cmd)
        t = time.time() - start
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

def process_config(config: str) -> Dict[str, str]:
    """
    Converts the string config produced by the fuzzer to a dictionary mapping options to settings.
    """
    i = 0
    tokens: List[str] = config.split(' ')
    result: Dict[str, str] = {}
    while(i < len(tokens)):
        if tokens[i].startswith('--'):
            if i == (len(tokens) - 1) or tokens[i+1].startswith('--'):
                result[tokens[i].replace('--', '')] = "TRUE"
                i = i + 1
            else:
                result[tokens[i].replace('--', '')] = tokens[i+1]
                i = i + 2
        else:
            i = i + 1 # skip
    return result


def mutate_config(model: Tool, config: Dict[str, str]):
    """
    For each option, consult the model for settings that are different.
    Add it to the configuration and randomly select one/some as a mutant.
    """
    candidates = list()
    options: List[Option] = model.get_options()

    for o in options:
#        import pdb; pdb.set_trace()
        for level in o.get_levels():
            if o.name not in config:
                config[o.name] = o.get_default()
            current_setting = config[o.name]
            if level == config[o.name]:
                 continue
            if (o.soundness_compare(level, config[o.name]) != 0):
                config_copy = copy.deepcopy(config)
                config_copy[o.name] = level
                candidates.append(config_copy)
    return candidates

if __name__ == '__main__':
    main()
