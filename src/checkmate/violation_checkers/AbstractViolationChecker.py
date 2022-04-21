import dataclasses
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Any

from src.checkmate.models.Option import Option
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation

logger = logging.getLogger(__name__)

class AbstractViolationChecker(ABC):

    def __init__(self, output: str):
        self.output: str = output

    def check_violations(self, results: List[FinishedFuzzingJob]) -> List[Violation]:
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
        self.summarize(violations)
        return violations
        # results_queue.task_done()

    def summarize(self, violations: List[Violation]):
        """
        Print a summary of the run.
        @param violations:
        @return: None
        """
        summary_struct = {}
        for v in violations:
            if v.get_partial_order() not in summary_struct:
                summary_struct[v.get_partial_order()] = {'pass': 0, 'fail': 0}
            if v.violated:
                summary_struct[v.get_partial_order()]['fail'] += 1
            else:
                summary_struct[v.get_partial_order()]['pass'] += 1
        keys = sorted(summary_struct.keys())
        print("Campaign Summary")
        print("------------------------")
        print("Partial Order\tPassed\tFailed")
        for k in keys:
            print(f'{k}\t{summary_struct[k]["pass"]}\t{summary_struct[k]["fail"]}')

    @abstractmethod
    def read_from_input(self, file: str) -> Any:
        pass

    @abstractmethod
    def is_more_precise(self, result1: Any, result2: Any) -> Violation:
        pass

    @abstractmethod
    def is_more_sound(self, result1: Any, result2: Any) -> Violation:
        pass
