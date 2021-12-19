import copy
import logging
import pickle
from random import random
from typing import List, Dict

from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar

from checkmate.fuzzing import flowdroid_grammar
from checkmate.fuzzing.flowdroid_grammar import FlowdroidGrammar
from checkmate.models.Option import Option
from checkmate.models.Tool import Tool
from checkmate.util import FuzzingPairJob


class FuzzGenerator:

    def __init__(self, model_location: str):
        self.flowdroid_ebnf_grammar = FlowdroidGrammar.getGrammar()
        self.flowdroid_grammar = convert_ebnf_grammar(self.flowdroid_ebnf_grammar)
        self.fuzzer = GrammarCoverageFuzzer(self.flowdroid_grammar)
        with open(model_location, 'rb') as f:
            self.model = pickle.load(f)

    def getNewPair(self) -> FuzzingPairJob:
        """
        This method generates the next task for the fuzzer.
        """
        fuzzed_config = self.process_config(self.fuzzer.fuzz())
        candidates = self.mutate_config(self.model, fuzzed_config)
        choice_tuple = random.choice(candidates)
        choice = choice_tuple[0]
        soundness_level = choice_tuple[1]
        option_under_investigation = [k for k in choice.keys() if
                                      k not in fuzzed_config.keys() or fuzzed_config[k] != choice[k]]

        f = FuzzingPairJob(fuzzed_config, choice, soundness_level, option_under_investigation)
        logging.DEBUG(f'Generated new job: {f}')
        return f

    def process_config(config: str) -> Dict[str, str]:
        """
        Converts the string config produced by the fuzzer to a dictionary mapping options to settings.
        """
        i = 0
        tokens: List[str] = config.split(' ')
        result: Dict[str, str] = {}
        while (i < len(tokens)):
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
                soundness_level = o.soundness_compare(level, config[o.name])
                if soundness_level != 0:
                    config_copy = copy.deepcopy(config)
                    config_copy[o.name] = level
                    candidates.append((config_copy, soundness_level))
        return candidates