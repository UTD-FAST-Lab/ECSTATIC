import copy
import logging
import os
import pickle
import random
from typing import List, Dict

from frozendict import frozendict
from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar, Grammar
from fuzzingbook.GreyboxFuzzer import Mutator, PowerSchedule
from fuzzingbook.GreyboxGrammarFuzzer import GreyboxGrammarFuzzer, FragmentMutator, LangFuzzer, RegionMutator
from fuzzingbook.Parser import EarleyParser

from checkmate.fuzzing.flowdroid_grammar import FlowdroidGrammar
from checkmate.models.Level import Level
from checkmate.models.Option import Option
from checkmate.models.Tool import Tool
from checkmate.util.FuzzingJob import FuzzingJob
from checkmate.util.NamedTuples import ConfigWithMutatedOption, FuzzingCampaign
from checkmate.util.config import configuration

logger = logging.getLogger(__name__)


def mutate_config(model: Tool, config: Dict[Option, Level]) -> List[ConfigWithMutatedOption]:
    """
    Given a configuration, generate every potential mutant of it that uses a configuration option in a partial
    order.
    """
    candidates: List[Dict[Option, Level]] = list()
    options: List[Option] = model.get_options()
    for o in options:
        for level in o.options_involved_in_partial_orders:
            if o not in config:
                config[o] = o.get_default()
            if level == config[o]:
                continue
            config_copy = copy.deepcopy(config)
            config_copy[o] = level
            candidates.append(ConfigWithMutatedOption(frozendict(config_copy), o))
    return candidates


def process_config(model: Tool, config: str) -> Dict[str, str]:
    """
    Converts the string config produced by the fuzzer to a dictionary mapping options to settings.
    """
    i = 0
    tokens: List[str] = config.split(' ')
    result: Dict[str, str] = {}
    while i < len(tokens):
        if tokens[i].startswith('--'):
            try:
                option: Option = \
                    [o for o in model.get_options() if o.name.lower() == tokens[i].replace('--', '').lower()][0]
            except IndexError:
                raise ValueError(
                    f'Configuration option {tokens[i].replace("--", "")} is not in the configuration space.')

            if i == (len(tokens) - 1) or tokens[i + 1].startswith('--'):
                result[option] = option.get_level("TRUE")
                i = i + 1
            else:
                result[option] = option.get_level(tokens[i + 1])
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

    FIRST_RUN = True

    def __init__(self, model_location: str):
        self.flowdroid_ebnf_grammar: Grammar = FlowdroidGrammar.get_grammar()
        self.flowdroid_grammar = convert_ebnf_grammar(self.flowdroid_ebnf_grammar)
        self.fuzzer = GrammarCoverageFuzzer(self.flowdroid_grammar)
        with open(model_location, 'rb') as f:
            self.model = pickle.load(f)

    def generate_campaign(self) -> FuzzingCampaign:
        """
        This method generates the next task for the fuzzer.
        """
        if FuzzGenerator.FIRST_RUN:
            logger.info("First run, returning default configuration.")
            fuzzed_config = process_config(self.model, FlowdroidGrammar.get_default())
            FuzzGenerator.FIRST_RUN = False
        else:
            while True:
                try:
                    config_to_try: str = self.fuzzer.fuzz()
                    fuzzed_config: Dict[str, str] = process_config(self.model, config_to_try)
                    break
                except ValueError as ve:
                    logger.warning(f'Produced config {config_to_try}, which is invalid. Trying again.')
        logger.info(f"Configuration is {str(fuzzed_config)}")
        candidates: List[ConfigWithMutatedOption] = mutate_config(self.model, fuzzed_config)
        logger.info(f"Generated {len(candidates)} single-option mutant configurations.")
        results: List[FuzzingJob] = list()
        candidates.append(ConfigWithMutatedOption(frozendict(fuzzed_config), None))

        for candidate in candidates:
            choice = candidate.config
            option_under_investigation = candidate.option
            apks = [a for a in get_apks(configuration['apk_location'])]
            for a in apks:
                results.append(FuzzingJob(choice, option_under_investigation, a))

        return FuzzingCampaign(results)
