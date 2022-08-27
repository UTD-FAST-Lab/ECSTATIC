#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
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
from typing import List, Dict, Tuple, Iterable, Any

from frozendict import frozendict
from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar

from src.ecstatic.models.Level import Level
from src.ecstatic.models.Option import Option
from src.ecstatic.models.Tool import Tool
from src.ecstatic.util.ConfigurationSpaceReader import ConfigurationSpaceReader
from src.ecstatic.util.PartialOrder import PartialOrder
from src.ecstatic.util.PotentialViolation import PotentialViolation
from src.ecstatic.util.UtilClasses import ConfigWithMutatedOption, FuzzingCampaign, Benchmark, BenchmarkRecord, \
    FuzzingJob
from src.ecstatic.util.Violation import Violation

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


class FuzzOptions(Enum):
    RANDOM = auto()
    GUIDED = auto()


class FuzzGenerator:

    def __init__(self, model_location: str,
                 grammar_location: str,
                 benchmark: Benchmark,
                 strategy: FuzzOptions = FuzzOptions.GUIDED,
                 full_campaigns: bool = False):
        self.first_run = True
        with open(grammar_location) as f:
            self.json_grammar = json.load(f)
        self.grammar = convert_ebnf_grammar(self.json_grammar)
        self.benchmark: Dict[BenchmarkRecord, int] = {b: 1 for b in benchmark.benchmarks}
        self.fuzzer = GrammarCoverageFuzzer(self.grammar)
        self.model = ConfigurationSpaceReader().read_configuration_space(model_location)
        self.strategy = strategy
        self.full_campaigns = full_campaigns

        self.partial_orders: Dict[PartialOrder, int] = {}
        for o in self.model.get_options():
            for p in o.partial_orders:
                self.partial_orders[p] = 1

        self.benchmark_population = {b: 1 for b in benchmark.benchmarks}

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

                if option.type.startswith('int'):
                    if not int(tokens[i + 1]):
                        raise ValueError(f"Expected {tokens[i + 1]} to be a number.")
                    if int(tokens[i + 1]) < option.min_value or int(tokens[i + 1]) > option.max_value:
                        result[option] = option.get_level(random.randint(option.min_value, option.max_value))
                    else:
                        result[option] = option.get_level(int(tokens[i + 1]))
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
        pass
        # if not self.adaptive:
        #     return  # Do nothing
        # # Else....
        # # For every violation, add the responsible option settings into the exclusion list.
        # for v in list(filter(lambda v: v.violated, violations)):
        #     v: Violation
        #     option: Option = v.get_option_under_investigation()
        #     self.exclusions.extend([v.job1.job.configuration[option], v.job2.job.configuration[option]])

    def make_new_seed(self) -> Dict[Option, Level]:
        """

        Returns
        -------

        """
        if self.first_run:
            return dict()
        else:
            config = ""
            while config == "":
                config = self.fuzzer.fuzz()
            return self.process_config(config)

    def generate_campaign(self) -> Tuple[FuzzingCampaign, Dict[Any, Any]]:
        """
        This method generates the next task for the fuzzer.
        """
        if len(self.partial_orders) == 0:
            print("All out of partial orders!")
            exit(0)
        seed_config = self.make_new_seed()
        seed_config = fill_out_defaults(self.model, seed_config)
        logger.info(f"Configuration is {[(str(k), str(v)) for k, v in seed_config.items()]}")
        results: List[FuzzingJob] = list()
        if self.first_run:
            candidate_sample = set()
            for o in self.model.options:
                for p in o.partial_orders:
                    candidate_sample.update(self.mutate_config(seed_config, p))
            # All candidates, all benchmarks
            candidate_sample.add(ConfigWithMutatedOption(seed_config, None, None))
            benchmarks_sample = self.benchmark_population.keys()
        else:
            candidate_sample = set()
            pos = set()
            if not self.full_campaigns:
                while len(pos) < min(len(self.partial_orders), 2):
                    pos.update(random.sample(self.partial_orders.keys(), 1,
                                             counts=self.partial_orders.values() if self.strategy is
                                                                                    FuzzOptions.GUIDED else None))
            else:
                # Use all partial orders.
                pos = self.partial_orders.keys()
            [candidate_sample.update(self.mutate_config(seed_config, p)) for p in pos]
            benchmarks_sample = set()

            if not self.full_campaigns:
                while len(benchmarks_sample) < min(4, len(self.benchmark_population)):
                    benchmarks_sample.update(random.sample(self.benchmark_population.keys(), 1,
                                                           counts=self.benchmark_population.values() if
                                                           self.strategy is FuzzOptions.GUIDED else None))
            else:
                benchmarks_sample = self.benchmark_population.keys()

            # Levels not selected
            held_out = [p for p in self.partial_orders if p not in pos]

            # Increase weight of all levels not selected
            for l in held_out:
                self.partial_orders[l] += 1

        for candidate in candidate_sample:
            choice = candidate.config
            # excluded = [v for k, v in choice.items() if v in self.exclusions]
            # if len(excluded) > 0:
            #     continue
            option_under_investigation = candidate.option
            for benchmark_record in benchmarks_sample:
                benchmark_record: BenchmarkRecord
                results.append(FuzzingJob(choice, option_under_investigation, benchmark_record))

        self.first_run = False
        state = {"seed": {str(k): str(v) for k, v in seed_config.items()},
                 "first_run": self.first_run,
                 "partial_orders": {str(k): str(v) for k, v in self.partial_orders.items()},
                 "benchmarks": {str(k): str(v) for k, v in self.benchmark.items()},
                 "partial_order_sample": [str(k) for k in candidate_sample],
                 "benchmarks_sample": [str(k) for k in benchmarks_sample]
                 }
        return FuzzingCampaign(results), state

    def feedback(self, violations: Iterable[PotentialViolation]):
            buggy_benchmarks = set()
            for v in [v for v in violations if v.is_violation and not v.is_transitive]:
                o: Option = v.get_option_under_investigation()

                # Don't retest levels that already exhibited violations.
                if o.type.lower().startswith('int'):
                    self.partial_orders = {p: w for p, w in self.partial_orders.items() if p.option != o}

                else:
                    self.partial_orders = {p: w for p, w in self.partial_orders.items() if p not in v.partial_orders}
                    # %del self.levels[v.job1.job.configuration[o]]
                    # del self.levels[v.job2.job.configuration[o]]

                # Weigh benchmarks higher that have discovered benchmarks.
                buggy_benchmarks.add(v.job1.job.target)
            # Increase weight of buggy benchmarks
            for k in self.benchmark.keys():
                if k in buggy_benchmarks:
                    self.benchmark_population[k] += 10
                else:
                    self.benchmark_population[k] = max(self.benchmark_population[k] - 1, 1)

    def mutate_config(self, config: Dict[Option, Level], partial_order) -> List[Tuple[ConfigWithMutatedOption, int]]:
        """
        Given a configuration, generate every potential mutant of it that uses a configuration option in a partial
        order.
        """
        candidates: List[ConfigWithMutatedOption] = list()
        for level in [partial_order.left, partial_order.right]:
            o = partial_order.option
            if o not in config:
                config[o] = o.get_default()
            if level == config[o]:
                continue
            if o.type.startswith('int'):
                if 'i' in level.level_name:
                    logging.info(f'Sampling between {o.min_value} and {o.max_value}')
                    level = Level(o.name, random.randint(o.min_value, o.max_value))
                    logging.info(f'Sampled level {str(level)}')
                else:
                    level = Level(o.name, int(level.level_name))
            config_copy = copy.deepcopy(config)
            config_copy[o] = level
            candidates.append((ConfigWithMutatedOption(frozendict(config_copy), o, level)))
        return candidates
