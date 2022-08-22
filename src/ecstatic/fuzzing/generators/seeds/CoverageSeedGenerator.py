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
import json
import logging
import random
import typing
from pathlib import Path
from typing import Dict

from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar

from src.ecstatic.models.Level import Level
from src.ecstatic.models.Option import Option
from src.ecstatic.util.ConfigurationSpaceReader import ConfigurationSpaceReader

Conf = Dict[Option, Level]

logger = logging.getLogger(__name__)


class CoverageSeedGenerator():
    def __init__(self, grammar_location: Path,
                 model_location: Path,
                 pool_size: int = 150):
        """
        :param grammar_location: The file location of the grammar.
        :param model_location: The location of the JSON configuration file.
        :param pool_size: The maximum size of seeds to pool.
        """
        with open(grammar_location, 'r') as f:
            grammar = convert_ebnf_grammar(json.load(f))
        self.model = ConfigurationSpaceReader().read_configuration_space(model_location)
        self.fuzzer = GrammarCoverageFuzzer(grammar)
        self.__pool: typing.List[Conf] = []
        self.pool_size = pool_size

    @property
    def pool(self) -> typing.List[Conf]:
        while len(self.__pool) < self.pool_size:
            self.__pool.append(self.process_config(self.fuzzer.fuzz()))
        return self.__pool

    def pick(self, measure: typing.Callable[[Conf], float] = lambda x: 1.0) -> Conf:
        """
        Return a configuration. If predicate is None,
        will return a random configuration out of the pool. Otherwise,
        will choose a configuration that maximizes the result of measure.
        :param measure: Some mapping from a configuration to a numeric value.
        :return: A configuration.
        """

        if measure is None:
            choice: Conf = random.choice(self.pool)
            self.pool.remove(choice)
        else:
            values = {p: measure(p) for p in self.pool}
            max_val: float = max(values.values())
            all_max = list(filter(lambda k, v: v == max_val, values.keys()))
            choice: Conf = random.choice(all_max)
            self.pool.remove(choice)
        return choice

    def process_config(self, config: str) -> Dict[Option, Level]:
        """
        Converts the string config produced by the fuzzer to a dictionary mapping options to settings.
        """
        logger.info(f"Fuzzed config is {config}")
        i = 0
        tokens: typing.List[str] = config.split(' ')
        result: Dict[Option, Level] = {}
        while i < len(tokens):
            if tokens[i].startswith('--'):
                try:
                    option: Option = \
                        [o for o in self.model.get_options() if o.name.lower() == tokens[i].replace('--', '').lower()][0]
                except IndexError:
                    raise ValueError(
                        f'Configuration option {tokens[i].replace("--", "")} is not in the configuration space.')

                if option.type.startswith('int'):
                    if not int(tokens[i+1]):
                        raise ValueError(f"Expected {tokens[i+1]} to be a number.")
                    if int(tokens[i+1]) < option.min_value or int(tokens[i+1]) > option.max_value:
                        result[option] = option.get_level(random.randint(option.min_value, option.max_value))
                    else:
                        result[option] = option.get_level(int(tokens[i+1]))
                if i == (len(tokens) - 1) or tokens[i + 1].startswith('--'):
                    result[option] = option.get_level("TRUE")
                    i = i + 1
                else:
                    result[option] = option.get_level(tokens[i + 1])
                    i = i + 2
            else:
                i = i + 1  # skip
        return result
