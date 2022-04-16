from dataclasses import dataclass
from typing import NamedTuple, Dict, Set, List, Any

from frozendict import frozendict

from src.checkmate.models.Flow import Flow
from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option


@dataclass
class BenchmarkRecord:
    name: str
    depends_on: List[str]
    sources: str

    def __init__(self, name: str, depends_on: List[str] = [], sources: str = None):
        self.name == name
        self.depends_on == depends_on
        self.sources == sources


@dataclass
class Benchmark:
    benchmarks: List[BenchmarkRecord]


class FuzzingJob:
    def __init__(self,
                 configuration: Dict[Option, Level],
                 option_under_investigation: Option | None,
                 target: BenchmarkRecord,
                 target_dependencies: List[str] = []):
        self.configuration = configuration
        self.option_under_investigation = option_under_investigation
        self.target = target

    def __eq__(self, other):
        return isinstance(other, FuzzingJob) and self.configuration == other.configuration and \
               self.option_under_investigation == other.option_under_investigation and \
               self.target == other.target and \
               self.target_dependencies == other.target_dependencies

    def as_dict(self) -> str:
        return {"option_under_investigation": self.option_under_investigation,
                "configuration": {f"{str(k)}: {str(v)}" for k, v in self.configuration.items()},
                "target": self.target,
                "target_dependencies": self.target_dependencies}


@dataclass
class FuzzingCampaign:
    jobs: List[FuzzingJob]


@dataclass
class ConfigWithMutatedOption:
    config: frozendict[str, str]
    option: Option | None


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
