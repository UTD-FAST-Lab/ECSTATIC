from typing import NamedTuple, Dict, Set, List

from frozendict import frozendict

from checkmate.models.Flow import Flow
from checkmate.models.Option import Option
from checkmate.util.FuzzingJob import FuzzingJob


class FuzzingCampaign(NamedTuple):
    jobs: List[FuzzingJob]


class ConfigWithMutatedOption(NamedTuple):
    config: frozendict[str, str]
    option: Option | None


class FinishedFuzzingJob(NamedTuple):
    job: FuzzingJob
    execution_time: float
    results_location: str
    configuration_location: str
    detected_flows: Dict[str, Set[Flow]]


class FinishedCampaign(NamedTuple):
    finished_jobs: List[FinishedFuzzingJob]
