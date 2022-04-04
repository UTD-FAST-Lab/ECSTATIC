import dataclasses
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Any

from src.checkmate.models.Option import Option
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation

logger = logging.getLogger("AbstractViolationChecker")


class AbstractViolationChecker(ABC):

    def __init__(self, output: str):
        self.output: str = output

    def check_violations(self, results: List[FinishedFuzzingJob]):
        violations: List[Violation] = []
        for finished_run in results:
            finished_run: FinishedFuzzingJob
            option_under_investigation: Option = finished_run.job.option_under_investigation
            # Find configs with potential partial order relationships.
            candidates: List[FinishedFuzzingJob]
            if option_under_investigation is None:
                candidates = [f for f in results if
                              f.job.target == finished_run.job.target and
                              f.results_location != finished_run.results_location]
            else:
                candidates = [f for f in results if
                              (f.job.option_under_investigation is None or
                               f.job.option_under_investigation == option_under_investigation) and
                              f.job.target == finished_run.job.target and
                              f.results_location != finished_run.results_location]
            logger.info(f'Found {len(candidates)} candidates for job {finished_run.results_location}')
            for candidate in candidates:
                candidate: FinishedFuzzingJob
                if finished_run.job.option_under_investigation is None:
                    # switch to the other candidate's
                    option_under_investigation = candidate.job.option_under_investigation
                    if option_under_investigation is None:
                        raise RuntimeError('Trying to compare two configurations with None as the option '
                                           'under investigation. This should never happen.')

                logger.info(f"option_under_investigation: {option_under_investigation.name}")
                candidate: FinishedFuzzingJob
                logger.info(f"finshed_run's config is {finished_run.job.configuration} {[f'{k}:{v}' for k, v in finished_run.job.configuration.items()]}")
                logger.info(f"candidate config is {candidate.job.configuration} {[f'{k}:{v}' for k, v in candidate.job.configuration.items()]}")
                if option_under_investigation.is_more_sound(
                        finished_run.job.configuration[option_under_investigation].level_name,
                        candidate.job.configuration[
                            option_under_investigation].level_name):  # left side is less sound than right side
                    violations.append(self.is_more_sound(finished_run, candidate))

                if option_under_investigation.is_more_precise(
                        finished_run.job.configuration[option_under_investigation].level_name,
                        candidate.job.configuration[
                            option_under_investigation].level_name):  # left side is less precise than right side
                    logger.info(f'{finished_run.job.configuration[option_under_investigation]} is more precise than or '
                                f'equal to {candidate.job.configuration[option_under_investigation]}')
                    violations.append(self.is_more_precise(finished_run, candidate))
        with open(self.output, 'w') as f:
            json.dump([v.as_dict() for v in violations], f)
        print(f'Finished checking violations. {len([v for v in violations if v.violated])} violations detected.')
        print('Campaign value processing done.')
        # results_queue.task_done()

    @abstractmethod
    def read_from_input(self, file: str) -> Any:
        pass

    @abstractmethod
    def is_more_precise(self, result1: Any, result2: Any) -> Violation:
        pass

    @abstractmethod
    def is_more_sound(self, result1: Any, result2: Any) -> Violation:
        pass