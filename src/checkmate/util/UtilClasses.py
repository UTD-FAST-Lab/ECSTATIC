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

from dataclasses import dataclass, field
from typing import Dict, Set, List, Any

from frozendict import frozendict

from src.checkmate.models.Flow import Flow
from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option


@dataclass
class BenchmarkRecord:
    name: str
    depends_on: List[str] = field(kw_only=True, default_factory=list)
    sources: List[str] = field(kw_only=True, default_factory=list)
    build_script: str = field(kw_only=True, default=None)
    packages: List[str] = field(kw_only=True, default_factory=list)

    def __hash__(self):
        return hash((self.name, tuple(self.depends_on), tuple(self.sources),
                     self.build_script, tuple(self.packages)))


@dataclass
class Benchmark:
    benchmarks: List[BenchmarkRecord]


class FuzzingJob:
    def __init__(self,
                 configuration: Dict[Option, Level],
                 option_under_investigation: Option | None,
                 target: BenchmarkRecord):
        self.configuration = configuration
        self.option_under_investigation = option_under_investigation
        self.target = target

    def __eq__(self, other):
        return isinstance(other, FuzzingJob) and self.configuration == other.configuration and \
               self.option_under_investigation == other.option_under_investigation and \
               self.target == other.target

    def as_dict(self) -> Dict[str, Any]:
        return {"option_under_investigation": self.option_under_investigation,
                "configuration": {f"{str(k)}: {str(v)}" for k, v in self.configuration.items()},
                "target": self.target}


@dataclass
class FuzzingCampaign:
    jobs: List[FuzzingJob]


@dataclass
class ConfigWithMutatedOption:
    config: frozendict[Option, Level]
    option: Option | None
    level: Level | None

    def __hash__(self):
        return hash((frozendict(self.config), self.option, self.level))


@dataclass
class FinishedFuzzingJob:
    job: FuzzingJob
    execution_time: float
    results_location: str


@dataclass
class FlowdroidFinishedFuzzingJob(FinishedFuzzingJob):
    configuration_location: str
    detected_flows: Dict[str, Set[Flow]]


@dataclass
class FinishedCampaign:
    finished_jobs: List[FinishedFuzzingJob]
