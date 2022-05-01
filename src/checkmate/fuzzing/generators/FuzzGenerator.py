#  CheckMate: A Configuration Tester for Static Analysis
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import copy
import json
import logging
import os
import random
from enum import Enum, auto
from typing import List, Dict, Iterable

from frozendict import frozendict
from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar

from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option
from src.checkmate.models.Tool import Tool
from src.checkmate.util.ConfigurationSpaceReader import ConfigurationSpaceReader
from src.checkmate.util.UtilClasses import ConfigWithMutatedOption, FuzzingCampaign, Benchmark, BenchmarkRecord, \
    FuzzingJob
from src.checkmate.util.Violation import Violation

random.seed(2001)
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

class SeedGenerationStrategy(Enum):
    COVERAGE = auto()
    RANDOM = auto()

class MutantWeighingStrategy(Enum):
    UNIFORM = auto()
    FIND_NEW_BUGS = auto()
    EXPLORE_EXISTING_BUGS = auto()

class BenchmarkSelectionStrategy(Enum):
    ALL = auto()
    NEW = auto()
    BUGGY= auto()

class FuzzGenerator:

    def __init__(self, model_location: str,
                 grammar_location: str,
                 benchmark: Benchmark,
                 seed_strategy: SeedGenerationStrategy = SeedGenerationStrategy.COVERAGE,
                 mutant_strategy: MutantWeighingStrategy = MutantWeighingStrategy.UNIFORM,
                 benchmark_strategy: BenchmarkSelectionStrategy = BenchmarkSelectionStrategy.ALL):
        self.first_run = True
        with open(grammar_location) as f:
            self.json_grammar = json.load(f)
        self.grammar = convert_ebnf_grammar(self.json_grammar)
        self.benchmark: Benchmark = benchmark
        self.fuzzer = GrammarCoverageFuzzer(self.grammar)
        self.model = ConfigurationSpaceReader().read_configuration_space(model_location)
        self.violations : Iterable[Violation] = []
        self.seed_strategy = seed_strategy
        self.mutant_strategy = mutant_strategy
        self.benchmark_strategy = benchmark_strategy

    def process_config(self, config: str) -> Dict[Option, Level]:
        """
        Converts the string config produced by the fuzzer to a dictionary mapping options to settings.
        """
        logger.info(f"Fuzzed config is {config}")
        i = 0
        tokens: List[str] = config.split(' ')
        result: Dict[Option, Level] = {}
        while i < len(tokens):
            if tokens[i].startswith('--'):
                try:
                    option: Option = \
                        [o for o in self.model.get_options() if o.name.lower() == tokens[i].replace('--', '').lower()][
                            0]
                except IndexError:
                    raise ValueError(
                        f'Configuration option {tokens[i].replace("--", "")} is not in the configuration space.')

                if option.type.startswith('int') and 'i' in tokens[i + 1]:
                    result[option] = Level(option.name, random.randint(option.min_value, option.max_value))
                if i == (len(tokens) - 1) or tokens[i + 1].startswith('--'):
                    result[option] = option.get_level("TRUE")
                    i = i + 1
                else:
                    result[option] = option.get_level(tokens[i + 1])
                    i = i + 2
            else:
                i = i + 1  # skip
        return result

    def update_exclusions(self, violations: List[Violation]):
        if not self.adaptive:
            return  # Do nothing
        # Else....
        # For every violation, add the responsible option settings into the exclusion list.
        for v in list(filter(lambda v: v.violated, violations)):
            v: Violation
            option: Option = v.get_option_under_investigation()
            self.exclusions.extend([v.job1.job.configuration[option], v.job2.job.configuration[option]])

    def make_new_seed(self) -> Dict[Option, Level]:
        """

        Returns
        -------

        """
        if self.first_run:
            self.first_run = False
            return dict()
        if self.seed_strategy == SeedGenerationStrategy.COVERAGE:
            config = ""
            while (config != ""):
                config = self.fuzzer.fuzz()
            return self.process_config(config)
        if self.seed_strategy == SeedGenerationStrategy.RANDOM:
            config = dict()
            for o in self.model.get_options():
                o: Option
                if o.type.startswith("int"):
                    config[o] = Level(o.name, random.randint(o.min_value, o.max_value))
                else:
                    config[o] = random.choice(o.get_levels())
            return config

    def generate_campaign(self) -> FuzzingCampaign:
        """
        This method generates the next task for the fuzzer.
        """
        seed_config = self.make_new_seed()
        seed_config = fill_out_defaults(self.model, seed_config)
        logger.info(f"Configuration is {[(str(k), str(v)) for k, v in seed_config.items()]}")
        candidates: List[ConfigWithMutatedOption] = self.mutate_config(seed_config)
        logger.info(f"Generated {len(candidates)} single-option mutant configurations.")
        results: List[FuzzingJob] = list()
        candidates.append(ConfigWithMutatedOption(frozendict(seed_config), None))

        for candidate in candidates:
            choice = candidate.config
            excluded = [v for k, v in choice.items() if v in self.exclusions]
            if len(excluded) > 0:
                continue
            logger.info(f"Chosen config: {choice}")
            option_under_investigation = candidate.option
            for benchmark_record in self.benchmark.benchmarks:
                benchmark_record: BenchmarkRecord
                results.append(FuzzingJob(choice, option_under_investigation, benchmark_record))

        return FuzzingCampaign(results)

    def mutate_config(self, config: Dict[Option, Level]) -> List[ConfigWithMutatedOption]:
        """
        Given a configuration, generate every potential mutant of it that uses a configuration option in a partial
        order.
        """
        candidates: List[ConfigWithMutatedOption] = list()
        options: List[Option] = self.model.get_options()
        for o in options:
            for level in o.get_levels_involved_in_partial_orders():
                try:
                    if o not in config:
                        config[o] = o.get_default()
                    if level == config[o]:
                        continue
                    if o.type.startswith('int'):
                        if 'i' in level.level_name:
                            level = Level(o.name, random.randint(o.min_value, o.max_value))
                        else:
                            level = Level(o.name, int(level.level_name))
                    config_copy = copy.deepcopy(config)
                    config_copy[o] = level
                    for _, v in config_copy.items():
                        if v in self.exclusions:
                            raise OptionExcludedError(f"Not allowed to use {v}")
                    candidates.append(ConfigWithMutatedOption(frozendict(config_copy), o))
                except OptionExcludedError as oee:
                    logger.debug(str(oee))
        return candidates
