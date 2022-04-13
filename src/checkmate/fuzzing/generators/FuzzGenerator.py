import copy
import json
import logging
import os
import pickle
import random
from typing import List, Dict

from frozendict import frozendict
from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar, Grammar

from src.checkmate.fuzzing.flowdroid_grammar import FlowdroidGrammar
from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.models.Tool import Tool
from src.checkmate.util.ConfigurationSpaceReader import ConfigurationSpaceReader
from src.checkmate.util.FuzzingJob import FuzzingJob
from src.checkmate.util.UtilClasses import ConfigWithMutatedOption, FuzzingCampaign
from src.checkmate.util.Violation import Violation
from src.checkmate.util.config import configuration

logger = logging.getLogger(__name__)


def fill_out_defaults(model: Tool, config: Dict[Option, Level]) -> Dict[Option, Level]:
    for o in model.get_options():
        logger.info(f"Config that we are filling out is {config}")
        if o not in config:
            config[o] = o.get_default()

    logger.info(f"Filled out config is {config}")
    return config

def get_apks(directory: str) -> List[str]:
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.apk'):
                yield os.path.join(root, f)

class OptionExcludedError(Exception):
    pass

class FuzzGenerator:
    FIRST_RUN = True

    def __init__(self, model_location: str, grammar_location: str, benchmarks: List[str],
                 no_adaptive: bool):
        with open(grammar_location) as f:
            self.json_grammar = json.load(f)
        self.grammar = convert_ebnf_grammar(self.json_grammar)
        self.benchmarks = benchmarks
        self.fuzzer = GrammarCoverageFuzzer(self.grammar)
        random.seed(2001)
        self.model = ConfigurationSpaceReader().read_configuration_space(model_location)
        self.no_adaptive = no_adaptive
        self.exclusions: List[Level] = []

    def process_config(self, config: str) -> Dict[Option, Level]:
        """
        Converts the string config produced by the fuzzer to a dictionary mapping options to settings.
        """
        logger.info(f"Fuzzed config is {config}")
        i = 0
        tokens: List[str] = config.split(' ')
        result: Dict[str, str] = {}
        while i < len(tokens):
            if tokens[i].startswith('--'):
                try:
                    option: Option = \
                        [o for o in self.model.get_options() if o.name.lower() == tokens[i].replace('--', '').lower()][0]
                except IndexError:
                    raise ValueError(
                        f'Configuration option {tokens[i].replace("--", "")} is not in the configuration space.')

                if i == (len(tokens) - 1) or tokens[i + 1].startswith('--'):
                    result[option] = option.get_level("TRUE")
                    i = i + 1
                else:
                    result[option] = option.get_level(tokens[i + 1])
                    i = i + 2
                if result[option] in self.exclusions:
                    """Raise a value error because the caller should handle what happens"""
                    raise OptionExcludedError(f"Could not add {str(result[option])} "
                                              f"because it is in the exclusions file.")
            else:
                i = i + 1  # skip
        return result

    def update_exclusions(self, violations: List[Violation]):
        if self.no_adaptive:
            return  # Do nothing
        # Else....
        # For every violation, add the responsible option settings into the exclusion list.
        for v in list(filter(lambda v: v.violated, violations)):
            v: Violation
            option: Option = v.get_option_under_investigation()
            self.exclusions.extend([v.job1.job.configuration[option], v.job2.job.configuration[option]])

    def generate_campaign(self) -> FuzzingCampaign:
        """
        This method generates the next task for the fuzzer.
        """
        if not FuzzGenerator.FIRST_RUN:
            logger.info("First run, returning default configuration.")
            fuzzed_config = dict()
            for o in self.model.get_options():
                o: Option
                if o.get_default() is not None:
                    fuzzed_config[o.name] = o.get_default().level_name()
            FuzzGenerator.FIRST_RUN = False
        else:
            while True:
                try:
                    config_to_try: str = self.fuzzer.fuzz()
                    fuzzed_config: Dict[Option, Level] = self.process_config(config_to_try)
                    break
                except ValueError as ve:
                    logger.warning(f'Produced config {config_to_try}, which is invalid. Trying again.')
                except OptionExcludedError as oee:
                    logger.warning("Fuzzer produced a configuration with an excluded value. Fuzzing again....")

        fuzzed_config = fill_out_defaults(self.model, fuzzed_config)
        logger.info(f"Configuration is {[(str(k), str(v)) for k, v in fuzzed_config.items()]}")
        candidates: List[ConfigWithMutatedOption] = self.mutate_config(fuzzed_config)
        logger.info(f"Generated {len(candidates)} single-option mutant configurations.")
        results: List[FuzzingJob] = list()
        candidates.append(ConfigWithMutatedOption(frozendict(fuzzed_config), None))

        for candidate in candidates:
            choice = candidate.config
            logger.info(f"Chosen config: {choice}")
            option_under_investigation = candidate.option
            for a in self.benchmarks:
                results.append(FuzzingJob(choice, option_under_investigation, a))

        return FuzzingCampaign(results)

    def mutate_config(self, config: Dict[Option, Level]) -> List[ConfigWithMutatedOption]:
        """
        Given a configuration, generate every potential mutant of it that uses a configuration option in a partial
        order.
        """
        candidates: List[Dict[Option, Level]] = list()
        options: List[Option] = self.model.get_options()
        for o in options:
            for level in o.get_levels_involved_in_partial_orders():
                try:
                    if o not in config:
                        config[o] = o.get_default()
                    if level == config[o]:
                        continue
                    config_copy = copy.deepcopy(config)
                    config_copy[o] = level
                    for _, v in config_copy.items():
                        if v in self.exclusions:
                            raise OptionExcludedError(f"Not allowed to use {v}")
                    candidates.append(ConfigWithMutatedOption(frozendict(config_copy), o))
                except OptionExcludedError as oee:
                    logger.debug(str(oee))
        return candidates

