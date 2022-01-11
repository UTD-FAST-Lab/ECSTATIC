import copy
import logging
import os
import pickle
import random
from typing import List, Dict

from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar
from fuzzingbook.GreyboxFuzzer import Mutator, PowerSchedule
from fuzzingbook.GreyboxGrammarFuzzer import GreyboxGrammarFuzzer, FragmentMutator
from fuzzingbook.Parser import EarleyParser

from checkmate.fuzzing.flowdroid_grammar import FlowdroidGrammar
from checkmate.models.Option import Option
from checkmate.models.Tool import Tool
from checkmate.util.FuzzingPairJob import FuzzingPairJob
from checkmate.util.config import configuration


def mutate_config(model: Tool, config: Dict[str, str]):
    """
    For each option, consult the model for settings that are different.
    Add it to the configuration and randomly select one/some as a mutant.
    """
    candidates = list()
    options: List[Option] = model.get_options()

    for o in options:
        for level in o.get_levels():
            if o.name not in config:
                config[o.name] = o.get_default()
            if level == config[o.name]:
                continue
            soundness_level = o.soundness_compare(level, config[o.name])
            if soundness_level != 0:
                config_copy = copy.deepcopy(config)
                config_copy[o.name] = level
                candidates.append((config_copy, soundness_level))
    return candidates


def process_config(config: str) -> Dict[str, str]:
    """
    Converts the string config produced by the fuzzer to a dictionary mapping options to settings.
    """
    i = 0
    tokens: List[str] = config.split(' ')
    result: Dict[str, str] = {}
    while i < len(tokens):
        if tokens[i].startswith('--'):
            if i == (len(tokens) - 1) or tokens[i + 1].startswith('--'):
                result[tokens[i].replace('--', '')] = "TRUE"
                i = i + 1
            else:
                result[tokens[i].replace('--', '')] = tokens[i + 1]
                i = i + 2
        else:
            i = i + 1  # skip
    return result


def get_apks(directory: str) -> List[str]:
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.apk'):
                yield os.path.join(root, f)


class FuzzGenerator:

    def __init__(self, model_location: str):
        self.flowdroid_ebnf_grammar = FlowdroidGrammar.getGrammar()
        self.flowdroid_grammar = convert_ebnf_grammar(self.flowdroid_ebnf_grammar)
        self.fuzzer = GreyboxGrammarFuzzer([FlowdroidGrammar.getDefault()], Mutator(), FragmentMutator(EarleyParser(self.flowdroid_grammar)),
                                           PowerSchedule())
        #self.fuzzer = GrammarCoverageFuzzer(self.flowdroid_grammar)
        with open(model_location, 'rb') as f:
            self.model = pickle.load(f)

    def get_new_pair(self) -> List[FuzzingPairJob]:
        """
        This method generates the next task for the fuzzer.
        """
        fuzzed_config = process_config(self.fuzzer.fuzz())
        candidates = mutate_config(self.model, fuzzed_config)
        results = list()

        for choice_tuple in candidates:
            choice = choice_tuple[0]
            soundness_level = choice_tuple[1]
            option_under_investigation = [k for k in choice.keys() if
                                          k not in fuzzed_config.keys() or fuzzed_config[k] != choice[k]]

            for a in get_apks(configuration['apk_location']):
                results.append(FuzzingPairJob(fuzzed_config, choice, soundness_level, option_under_investigation, a))
        # logging.debug(f'Generated new job:')
        return results
