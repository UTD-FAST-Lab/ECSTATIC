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


import importlib
import os

import pytest

from src.ecstatic.fuzzing.generators.FuzzGenerator import FuzzGenerator
from src.ecstatic.fuzzing.generators.SOOTFuzzGenerator import SOOTFuzzGenerator
from src.ecstatic.models.Level import Level
from src.ecstatic.util.UtilClasses import Benchmark, BenchmarkRecord, FuzzingCampaign, FuzzingJob

b: Benchmark = Benchmark([BenchmarkRecord(
    os.path.abspath(importlib.resources.path("src.resources.benchmarks.test", "CallSiteSensitivity1.jar")))])


@pytest.mark.parametrize("tool", ["soot", "wala", "doop"])
def test_FuzzGenerator_first_run(tool: str):
    fg: FuzzGenerator = FuzzGenerator(
        importlib.resources.path("src.resources.configuration_spaces", f"{tool}_config.json"),
        importlib.resources.path("src.resources.grammars", f"{tool}_grammar.json"),
        b)
    campaign: FuzzingCampaign = fg.generate_campaign()
    for c in campaign.jobs:
        c: FuzzingJob
        val = len([k for k in c.configuration if c.configuration[k] != k.get_default()])
        assert val < 2


@pytest.mark.parametrize("tool,excluded_level", [("soot", Level("optimize", "TRUE")),
                                                 ("wala", Level("cgalgo", "ZERO_CFA")),
                                                 ("doop", Level("analysis", "1-object-sensitive"))])
def test_FuzzGenerator_exclusion(tool: str, excluded_level: Level):
    fg: FuzzGenerator = FuzzGenerator(
        importlib.resources.path("src.resources.configuration_spaces", f"{tool}_config.json"),
        importlib.resources.path("src.resources.grammars", f"{tool}_grammar.json"),
        b) if tool != "soot" else SOOTFuzzGenerator(
        importlib.resources.path("src.resources.configuration_spaces", f"{tool}_config.json"),
        importlib.resources.path("src.resources.grammars", f"{tool}_grammar.json"), b)
    campaign: FuzzingCampaign = fg.generate_campaign()
    fg.exclusions.append(excluded_level)
    campaign: FuzzingCampaign = fg.generate_campaign()
    for c in campaign.jobs:
        assert len([v for k, v in c.configuration.items() if v == excluded_level]) == 0
