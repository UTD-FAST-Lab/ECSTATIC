import logging
logging.basicConfig(level = logging.CRITICAL)

import xml.etree.ElementTree as ET
from Flow import Flow
from Configuration import Configuration
from checkmate.models.Constraint import Constraint 
from checkmate.models.Option import Option
from checkmate.models.Level import Level
from checkmate.models.Tool import Tool
from typing import List, Dict
from csv import DictReader
import pickle
import os

import argparse
p = argparse.ArgumentParser()
p.add_argument('groundtruths',
               help="""The file in AQL-Answer format that stores \
               the ground truths embedded as <classification> tags.""")
p.add_argument('--config_file',
               default='../../../tools/config/FlowDroid/flowdroid_1way.csv',
               help="""The CSV file mapping configuration
               names to their configurations. (See default value for an example.)""")
p.add_argument('files_list', nargs='+',
               help="""A file containing the list of raw data files to check. The script \
               can accept multiple files here, each of which is analyzed separately. \
               Violations will only be detected between two files that are in the same input list. \
               This is useful for checking multiple replications at once. """)
p.add_argument('--write_files', action='store_true',
               help="""If enabled, we will overwrite result files \
               with the classifications.""")
p.add_argument('--verify_classifications', action='store_true',
               help="""If enabled, the script will check \
               any existing classification tags for correctness \
               and fix any errors. Otherwise, it will simply \
               skip checking classifications for any flow \
               that already has groundtruths.""")
p.add_argument('--data_directory', default='./checkmate/data',
               help="""The directory in which checkmate's model files \
               are stored.""")
np.add_argument('--tool', default='flowdroid', choices=['flowdroid','droidsafe'],
               help="""The tool that we are checking for violations in.""")
p.add_argument('--dataset', default='fossdroid', choices=['fossdroid', 'droidsafe'],
               help="""The dataset these reports are from.""")
p.add_argument('--violation_location', default='./violations',
               help="""Where to store violations.""")
p.add_argument('--no_deltadebugger_output', action='store_true',
               help="""If this option is enabled, the program will not output the formats that are required
               by the delta debugger.""")
args = p.parse_args()

DEFAULT_CONFIG = {'flowdroid': 'aplength5', 'droidsafe': 'kobjsens3'}
TIMEOUTS = {'fossdroid': 7200000, 'droidbench': 600000}

def check_args():
    """
    Sanity checks for arguments. Throws exceptions if any arguments are
    incorrect.
    """
    if len(args.files_list) <= 1:
        raise RuntimeError('Must supply at least two files.')
    if args.dataset != 'fossdroid':
        raise RuntimeError('Currently this tool only supports FossDroid.')

def add_classifications(groundtruths: str, files_list: List[str],
                        verify_classifications: bool, write_files: bool,
                        dataset: str) -> Dict[str, Flow]:
    """
    Opens the groundtruths and flow file and adds in classifications.
    """
    # Open the groundtruths
    groundtruths : List[Flow] = [Flow(f) for f in ET.parse(args.groundtruths).getroot().iter('flow')]
    
    # Open each file.
    files_to_flows : Dict[str, List[Dict]] = dict()
    for f in files_list:
        # Save the root
        logging.debug(f'Opening {f}')
        root : ElementTree.Element = ET.parse(f).getroot()
        if float(root.get('time')) > TIMEOUTS[dataset]:
            continue # we do not want to add timeouts.

        files_to_flows[f] : List[Flow] = [Flow(f) for f in root.iter('flow')]
        # Go through each flow and check if it already
        #  has classifications.
        to_remove : List[Flow] = list()
        for g in files_to_flows[f]:
            if g.get_classification() is not None and\
               not verify_classifications:
                # unless verify_classifications is on,
                #  we will just skip these.
                continue
            if g not in groundtruths:
                logging.warn(f'Flow with source and sink {g.get_source_and_sink()} '
                                 'is not in groundtruths.')
                to_remove.append(g)
            else:
                # Add in the classification
                gt : Flow = groundtruths[groundtruths.index(g)]
                classifications : List[ElementTree.Element] = [e for e in gt.element.iter('classification')]
                if len(classifications) > 1:
                    id : int = gt[0].get('id')
                    if id is not None:
                        raise RuntimeError(f'Groundtruth with id {id} has more than '
                                           'one classification.')
                    else:
                        raise RuntimeError(f'A groundtruth with no id has more than '
                                           'one classification. That really stinks.')
                elif len(classifications) < 0:
                    id : int = gt[0].get('id')
                    if id is not None:
                        raise RuntimeError(f'Groundtruth with id {id} has no classification.')
                    else:
                        raise RuntimeError(f'A groundtruth with no id has no '
                                           'classification. That really stinks.')
                else:
                    g.add_classification(classifications[0].text)
        if len(to_remove) > 0:
            logging.warn(f'Now removing {len(to_remove)} flows that could not be classified.')
            for t in to_remove:
                files_to_flows[f].remove(t)


    logging.info('Added all classifications.')
    if write_files:
        logging.critical('Writing files is not yet supported. Sorry!')

    logging.debug('Returning from add_classifications.')
    return files_to_flows

def get_option_under_investigation(k: str) -> str:
    """
    Takes the configuration name and returns the option
    that the configuration is investigating.
    """
    if k.startswith('config_'):
        k : str = k.replace('config_', '')
    if k.endswith('.xml'):
        k : str = k.replace('.xml', '')

    options_map = {
        'aliasalgofs' : 'aliasalgo',
        'aliasalgolazy' : 'aliasalgo',
        'aliasalgonone' : 'aliasalgo',
        'aliasalgoptsbased' : 'aliasalgo',
        'aliasflowins' : 'aliasflowins',
        'analyzeframeworks' : 'analyzeframeworks',
        'aplength1' : 'aplength',
        'aplength10' : 'aplength',
        'aplength2' : 'aplength',
        'aplength20' : 'aplength',
        'aplength3' : 'aplength',
        'aplength4' : 'aplength',
        'aplength5' : 'aplength',
        'aplength7' : 'aplength',
        'callbackanalyzerdef' : 'callbackanalyzer',
        'callbackanalyzerfast' : 'callbackanalyzer',
        'cgalgoauto' : 'cgalgo',
        'cgalgocha' : 'cgalgo',
        'cgalgogeom' : 'cgalgo',
        'cgalgorta' : 'cgalgo',
        'cgalgospark' : 'cgalgo',
        'cgalgovta' : 'cgalgo',
        'codeeliminationnone' : 'codeelimination',
        'codeeliminationpc' : 'codeelimination',
        'codeeliminationrc' : 'codeelimination',
        'dataflowsolvercsfs' : 'dataflowsolver',
        'dataflowsolverfins' : 'dataflowsolver',
        'enablereflection' : 'enablereflection',
        'implicitall' : 'implicit',
        'implicitarronly' : 'implicit',
        'implicitnone' : 'implicit',
        'maxcallbackchain0' : 'maxcallbacksdepth',
        'maxcallbackchain1' : 'maxcallbacksdepth',
        'maxcallbackchain100' : 'maxcallbacksdepth',
        'maxcallbackchain110' : 'maxcallbacksdepth',
        'maxcallbackchain120' : 'maxcallbacksdepth',
        'maxcallbackchain150' : 'maxcallbacksdepth',
        'maxcallbackchain200' : 'maxcallbacksdepth',
        'maxcallbackchain50' : 'maxcallbacksdepth',
        'maxcallbackchain600' : 'maxcallbacksdepth',
        'maxcallbackchain80' : 'maxcallbacksdepth',
        'maxcallbackchain90' : 'maxcallbacksdepth',
        'maxcallbacks1' : 'maxcallbackspercomponent',
        'maxcallbacks100' : 'maxcallbackspercomponent',
        'maxcallbacks110' : 'maxcallbackspercomponent',
        'maxcallbacks120' : 'maxcallbackspercomponent',
        'maxcallbacks150' : 'maxcallbackspercomponent',
        'maxcallbacks200' : 'maxcallbackspercomponent',
        'maxcallbacks50' : 'maxcallbackspercomponent',
        'maxcallbacks600' : 'maxcallbackspercomponent',
        'maxcallbacks80' : 'maxcallbackspercomponent',
        'maxcallbacks90' : 'maxcallbackspercomponent',
        'nocallbacks' : 'nocallbacks',
        'noexceptions' : 'noexceptions',
        'nothischainreduction' : 'nothischainreduction',
        'onecomponentatatime' : 'onecomponentatatime',
        'onesourceatatime' : 'onesourceatatime',
        'pathalgocontextinsensitive' : 'pathalgo',
        'pathalgocontextsensitive' : 'pathalgo',
        'pathalgosourcesonly' : 'pathalgo',
        'pathspecificresults' : 'pathspecificresults',
        'singlejoinpointabstraction' : 'singlejoinpointabstraction',
        'staticmodecsfs' : 'staticmode',
        'staticmodefins' : 'staticmode',
        'staticmodenone' : 'staticmode',
        'taintwrapperdefaultfallback' : 'taintwrapper',
        'taintwrappereasy' : 'taintwrapper',
        'taintwrappernone' : 'taintwrapper',
        'analyzestringsunfiltered' : 'analyzestringsunfiltered',
        'apicalldepth0' : 'apicalldepth',
        'apicalldepth1' : 'apicalldepth',
        'apicalldepth100' : 'apicalldepth',
        'apicalldepth110' : 'apicalldepth',
        'apicalldepth120' : 'apicalldepth',
        'apicalldepth150' : 'apicalldepth',
        'apicalldepth200' : 'apicalldepth',
        'apicalldepth50' : 'apicalldepth',
        'apicalldepth600' : 'apicalldepth',
        'apicalldepth80' : 'apicalldepth',
        'apicalldepth90' : 'apicalldepth',
        'filetransforms' : 'filetransforms',
        'ignoreexceptionflows' : 'ignoreexceptionflows',
        'ignorenocontextflows' : 'ignorenocontextflows',
        'implicitflow' : 'implicitflows',
        'imprecisestrings' : 'imprecisestrings',
        'kobjsens1' : 'kobjsens',
        'kobjsens18' : 'kobjsens',
        'kobjsens2' : 'kobjsens',
        'kobjsens3' : 'kobjsens',
        'kobjsens4' : 'kobjsens',
        'kobjsens5' : 'kobjsens',
        'kobjsens6' : 'kobjsens',
        'limitcontextforcomplex' : 'limitcontextforcomplex',
        'limitcontextforgui' : 'limitcontextforgui',
        'limitcontextforstrings' : 'limitcontextforstrings',
        'multipassfb' : 'multipassfb',
        'noarrayindex' : 'noarrayindex',
        'noclinitcontext' : 'noclinitcontext',
        'noclonestatics' : 'noclonestatics',
        'nofallback' : 'nofallback',
        'nojsa' : 'nojsa',
        'noscalaropts' : 'noscalaropts',
        'nova' : 'nova',
        'preciseinfoflow' : 'preciseinfoflow',
        'ptageo' : 'pta',
        'ptapaddle' : 'pta',
        'ptaspark' : 'pta',
        'transfertaintfield' : 'transfertaintfield',
        'typesforcontext' : 'typesforcontext'
    }

    if k not in options_map:
        raise RuntimeError(f'Cannot map {k} to the option under investigation.')
    else:
        return options_map[k]

def add_configurations(files_to_flows: Dict[str, List[Flow]],
                       settings_file: str) -> Dict[Configuration, Flow]:
    """
    Replaces the configuration name with a configuration object.
    """
    # Load in the settings.
    with open(settings_file) as f:
        reader : DictReader = DictReader(f)
        settings : Dict[str, Dict] = {r['file'].replace('config_','').strip(','): r for r in reader}

    logging.debug(settings.keys())
    configurations_to_flows : Dict[Configuration, Flow] = dict()
        
    file: str
    files_to_flows: List[Flow]
    for file, flows in files_to_flows.items():
        candidates = {k: v for k,v in settings.items() if f'{k}.xml' in file}
        if len(candidates) > 1:
            raise RuntimeError(f'Found multiple matching settings for {file}.')
        elif len(candidates) == 0:
            raise RuntimeError(f'Could not find the configuration for {file}.')
        else: # len(candidates) == 1
            k : str
            v : Dict[str, Dict]
            for k, v in candidates.items(): # only one
                c = Configuration(get_option_under_investigation(k), v, k, file)
                configurations_to_flows[c] = flows

    return configurations_to_flows

def check_for_violations(configurations_to_flows: Dict[Configuration, List[Flow]],
                         tool: str, data_directory: str, violation_directory: str,
                         suffix: str):
    """
    Opens the model file and checks for any violations.
    """
    with open(os.path.join(data_directory, f'{tool}.model'), 'rb') as f:
        model : Tool = pickle.load(f)

    config1: Configuration
    listflows1: List[Flow]
    for config1, listflows1 in configurations_to_flows.items():
        for config2, listflows2 in configurations_to_flows.items():
            if config1 == config2:
                continue
            elif config1.config_file != config2.config_file and\
                 config1.apk == config2.apk and\
                 (config1.option_under_investigation == config2.option_under_investigation or\
                  (config1.config_file == DEFAULT_CONFIG[tool] or\
                 config2.config_file == DEFAULT_CONFIG[tool])):
                # Either the two options are the same or one is default.
                # First, we need to detect the different settings.
                oui : str
                if config1.config_file == DEFAULT_CONFIG[tool]:
                    oui = config2.option_under_investigation
                else:
                    oui = config1.option_under_investigation
                try:
                    option : Option = [o for o in model.get_options() if o.name == oui][0]
                except IndexError:
                    raise RuntimeError(f'{oui} is not in the model.')
                for t in ['precision', 'soundness']:
                    fnc = option.precision_compare if t == 'precision' else option.soundness_compare
                    if fnc(config1.configuration[oui],config2.configuration[oui]) > 0:
                        logging.info(f'{config1.configuration[oui]} has more {t} than '
                                     f'{config2.configuration[oui]}')
                        if t == 'soundness':
                            tp1 : Set[Flow] = set([f for f in listflows1 if \
                                                   f.get_classification().upper() == 'TRUE'])
                            logging.debug(f'Length of tp1 is {len(tp1)}.')
                            tp2 : Set[Flow] = set([f for f in listflows2 if \
                                                   f.get_classification().upper() == 'TRUE'])
                            logging.debug(f'Length of tp2 is {len(tp2)}.')
                            comparison_set : Set[Flow] = tp2.difference(tp1)
                            provenance = config2.config_file
                        elif t == 'precision':
                            fp1 : Set[Flow] = set([f for f in listflows1 if \
                                                   f.get_classification().upper() == 'FALSE'])
                            logging.debug(f'Length of fp1 is {len(fp1)}.')
                            fp2 : Set[Flow] = set([f for f in listflows2 if \
                                                   f.get_classification().upper() == 'FALSE'])
                            logging.debug(f'Length of fp2 is {len(fp2)}.')
                            comparison_set : Set[Flow] = fp1.difference(fp2)
                            provenance = config1.config_file

                        if len(comparison_set) > 0:
                            print(f'Violation ({t}) found between {oui} settings '
                                  f'{config1.configuration[oui]} and '
                                  f'{config2.configuration[oui]} in '
                                  f'{" ".join([str(f) for f in comparison_set])}')
                            violation : ET.Element = ET.Element('flowset')
                            violation.set('violation', 'True')
                            violation.set('type', t)
                            violation.set('config1', config1.config_file)
                            violation.set('config2', config2.config_file)
                            preserve : ET.Element = ET.Element('preserve')
                            preserve.set('config', provenance)
                            f: Flow
                            for f in comparison_set:
                                preserve.append(f.element)
                            if not os.path.exists(violation_directory):
                                os.makedirs(violation_directory)
                            violation.append(preserve)
                            fname = f'flowset_violation-true_{t}_{config1.apk}'\
                                    f'_{config1.option_under_investigation}_'\
                                    f'{config1.configuration[oui]}_{config2.option_under_investigation}_'\
                                    f'{config2.configuration[oui]}_{suffix}.xml'
                            # Output to file.
                            tree = ET.ElementTree(violation)
                            tree.write(os.path.join(violation_directory, fname))
                        else:
                            if args.no_deltadebugger_output:
                                continue
                            print(f'No violation ({t}) found between {oui} settings '
                                  f'{config1.configuration[oui]} and '
                                  f'{config2.configuration[oui]}.')
                            violation : ET.Element = ET.Element('flowset')
                            violation.set('violation', 'False')
                            violation.set('type', t)
                            violation.set('config1', config1.config_file)
                            violation.set('config2', config2.config_file)
                            f: Flow
                            # Here, we want to output the set of true and false flows
                            #  so that the delta debugger can minimize.
                            if t == 'precision':
                                set1 : Set[Flow] = fp1
                                set2 : Set[Flow] = fp2
                            elif t == 'soundness':
                                set1 : Set[Flow] = tp1
                                set2 : Set[Flow] = tp2

                            for s, provenance in [(set1, config1.config_file),
                                                  (set2, config2.config_file)]:
                                preserve : ET.Element = ET.Element('preserve')
                                preserve.set('config', provenance)
                                for f in s:
                                    preserve.append(f.element)
                                violation.append(preserve)
                            if not os.path.exists(violation_directory):
                                os.makedirs(violation_directory)
                            fname = f'flowset_violation-false_{t}_{config1.apk}'\
                                    f'_{config1.option_under_investigation}_'\
                                    f'{config1.configuration[oui]}_{config2.option_under_investigation}_'\
                                    f'{config2.configuration[oui]}_{suffix}.xml'
                            # Output to file.
                            tree = ET.ElementTree(violation)
                            tree.write(os.path.join(violation_directory, fname))

def main():
    # Check that the arguments are correct.
    check_args()
    logging.info('Argument sanity check passed.')

    for i, single_file in enumerate(args.files_list):
        with open(single_file) as f:
            files_list = [l.strip() for l in f.readlines()]
        files_to_flows: Dict[str, List[Flow]] = add_classifications(args.groundtruths, files_list,
                                                                args.verify_classifications,
                                                                args.write_files,
                                                                args.dataset)
        configurations_to_flows: Dict[Configuration, List[Flow]] = add_configurations(files_to_flows,
                                                                                  args.config_file)
        check_for_violations(configurations_to_flows, args.tool, args.data_directory, args.violation_location, str(i))
        

if __name__ == '__main__':
    main()
