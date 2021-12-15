import time

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
        print(f'Pair of configs is {fuzzed_config}, {choice}. Different on {[k for k in choice.keys() if k not in fuzzed_config.keys() or fuzzed_config[k] != choice[k]]}.')
        for c in [fuzzed_config, choice]:
            c_str = dict_to_config_str(c)
            shell_location = create_shell_file(c_str)
            xml_location = create_xml_config_file(shell_location)
            for a in get_apks(config.configuration['apk_location']):
                run_aql(a, xml_location)



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
    content = map(lambda r: r.replace('%FLOWDROID_HOME%', config.configuration['flowdroid_location']), content)
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
            element.text = os.path.abspath(config.configuration["flowdroid_location"])
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
            xml_config_file: str):
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
        cmd = ["java", "-jar", os.path.abspath(config.configuration['aql_location']), "-t", "2h",
               "-reset", "-c", os.path.abspath(xml_config_file), "-q",
               "\"Flows IN App('", os.path.abspath(apk), "') ?\"", "-o", output]
        cur = os.curdir
        os.chdir(os.path.dirname(config.configuration['aql_location']))
        cp = subprocess.run(cmd, capture_output=True)
        os.chdir(cur)
        tree = ET.parse(output)
        root = tree.getroot()
        root.set("time", str(t))

        tree.write(output)

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
