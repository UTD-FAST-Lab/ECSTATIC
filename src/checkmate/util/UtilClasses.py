from dataclasses import dataclass
from typing import NamedTuple, Dict, Set, List, Any

from frozendict import frozendict

from src.checkmate.models.Flow import Flow
from src.checkmate.models.Option import Option
from src.checkmate.util.FuzzingJob import FuzzingJob


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

@dataclass
class Violation:
    violated: bool
    type: str
    config1: str
    results1: str
    config2: str
    results2: str
    option_under_investigation: str
    target: str
    differences: List[str]