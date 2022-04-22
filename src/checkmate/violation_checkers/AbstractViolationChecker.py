import json
import logging
import time
from abc import ABC, abstractmethod
from multiprocessing import Pool
from typing import List, Any, Tuple, Set, Iterable, TypeVar

import jsonpickle as jsonpickle

from src.checkmate.models.Option import Option
from src.checkmate.util.PartialOrder import PartialOrder, PartialOrderType
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation

logger = logging.getLogger(__name__)
T = TypeVar('T')  # Indicates the type of content in the results (e.g., call graph edges or flows)


class AbstractViolationChecker(ABC):

    def __init__(self, output: str, jobs: int, groundtruths: str | None = None):
        self.output: str = output
        self.jobs: int = jobs
        self.groundtruths = groundtruths

    def check_violations(self, results: List[FinishedFuzzingJob]) -> List[Violation]:
        start_time = time.time()
        pairs: List[Tuple[FinishedFuzzingJob, FinishedFuzzingJob, Option]] = []
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

                pairs.append((finished_run, candidate, option_under_investigation))

        violations = []
        with Pool(self.jobs) as p:
            print(f'Checking violations with {self.jobs} cores.')
            [violations.extend(v_set) for v_set in p.starmap(self.check_for_violation, pairs)]

            # logger.info(f"option_under_investigation: {option_under_investigation.name}")
            # candidate: FinishedFuzzingJob
            # logger.info(
            #     f"finshed_run's config is {finished_run.job.configuration} {[f'{k}:{v}' for k, v in finished_run.job.configuration.items()]}")
            # logger.info(
            #     f"candidate config is {candidate.job.configuration} {[f'{k}:{v}' for k, v in candidate.job.configuration.items()]}")
            # if option_under_investigation.is_more_sound(
            #         finished_run.job.configuration[option_under_investigation].level_name,
            #         candidate.job.configuration[
            #             option_under_investigation].level_name):  # left side is less sound than right side
            #     violations.append(self.is_more_sound(finished_run, candidate))
            #
            # if option_under_investigation.is_more_precise(
            #         finished_run.job.configuration[option_under_investigation].level_name,
            #         candidate.job.configuration[
            #             option_under_investigation].level_name):  # left side is less precise than right side
            #     logger.info(f'{finished_run.job.configuration[option_under_investigation]} is more precise than or '
            #                 f'equal to {candidate.job.configuration[option_under_investigation]}')
            #     violations.append(self.is_more_precise(finished_run, candidate))
        with open(self.output, 'w') as f:
            encoded = jsonpickle.encode(violations)
            json.dumps(encoded, f, indent=4)
        print(f'Finished checking violations. {len([v for v in violations if v.violated])} violations detected.')
        print(f'Campaign value processing done (took {time.time() - start_time} seconds).')
        self.summarize(violations)
        return violations
        # results_queue.task_done()

    def summarize(self, violations: Iterable[Violation]):
        """
        Print a summary of the run.
        @param violations:
        @return: None
        """
        summary_struct = {}
        for v in violations:
            if v.get_option_under_investigation() not in summary_struct:
                summary_struct[v.get_option_under_investigation()] = 0
            summary_struct[v.get_option_under_investigation()] += 1
        keys = sorted(summary_struct.keys())
        print("Campaign Summary")
        # print(f"Total Time: {sum(time_struct.values())}s")
        # print(f"Average Time: {sum(time_struct.values()) / float(len(time_struct.values()))}s")
        # print(f"Max Time: {max(time_struct.values())}s")
        print("------------------------")
        print("Option (Number of Violations)")
        for k in keys:
            print(f'{k} ({summary_struct[k]})')

    @abstractmethod
    def get_true_positives(self, input: Any) -> Set[T]:
        pass

    @abstractmethod
    def get_false_positives(self, input: Any) -> Set[T]:
        pass

    @abstractmethod
    def read_from_input(self, file: str) -> Iterable[T]:
        pass

    def check_for_violation(self, job1: FinishedFuzzingJob,
                            job2: FinishedFuzzingJob,
                            option_under_investigation: Option) -> Iterable[Violation]:
        """
        Given two jobs, checks whether there are any violations.
        Parameters
        ----------
        job1: The first job to check.
        job2: The second job to check.
        option_under_investigation: The option on which the two jobs differ.

        Returns
        -------
        An iterable containing any violations that were detected (can be empty).
        """
        results = []
        if self.groundtruths is None:
            # In the absence of ground truths, we have to compute violations differently.
            if option_under_investigation.is_more_sound(job1.job.configuration[option_under_investigation],
                                                        job2.job.configuration[option_under_investigation]):
                if option_under_investigation.is_more_precise(job2.job.configuration[option_under_investigation],
                                                              job1.job.configuration[option_under_investigation]):
                    # If these are true, and job2 has more stuff than job1, we have a certain violation of one of these
                    # partial orders.
                    differences: Set[T] = set(self.read_from_input(job2.results_location)).difference(
                        set(self.read_from_input(job1.results_location)))
                    if len(differences) > 0:
                        pos: Set[PartialOrder] = {PartialOrder(job1.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_SOUND_THAN,
                                                               job2.job.configuration[option_under_investigation]),
                                                  PartialOrder(job2.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_PRECISE_THAN,
                                                               job1.job.configuration[option_under_investigation])}
                        results.append(Violation(True, pos, job1, job2, differences))
            if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                          job2.job.configuration[option_under_investigation]):
                if option_under_investigation.is_more_sound(job2.job.configuration[option_under_investigation],
                                                            job1.job.configuration[option_under_investigation]):
                    differences: Set[T] = set(self.read_from_input(job1.results_location)).difference(
                        set(self.read_from_input(job2.results_location)))
                    if len(differences) > 0:
                        pos: Set[PartialOrder] = {PartialOrder(job1.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_PRECISE_THAN,
                                                               job2.job.configuration[option_under_investigation]),
                                                  PartialOrder(job2.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_SOUND_THAN,
                                                               job1.job.configuration[option_under_investigation])}
                        results.append(Violation(True, pos, job1, job2, differences))
        else:
            if option_under_investigation.is_more_sound(job1.job.configuration[option_under_investigation],
                                                        job2.job.configuration[option_under_investigation]):
                differences: Set[T] = self.get_true_positives(self.read_from_input(job2.results_location)).difference(
                    self.get_true_positives(self.read_from_input(job1.results_location)))
                if len(differences) > 0:
                    results.append(Violation(True, {PartialOrder(job1.job.configuration[option_under_investigation],
                                                                 PartialOrderType.MORE_SOUND_THAN,
                                                                 job2.job.configuration[option_under_investigation])},
                                             job1, job2, differences))
            if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                          job2.job.configuration[option_under_investigation]):
                differences: Set[T] = self.get_false_positives(self.read_from_input(job1.results_location)).difference(
                    self.get_false_positives(self.read_from_input(job2.results_location)))
                if len(differences) > 0:
                    results.append(Violation(True, {PartialOrder(job1.job.configuration[option_under_investigation],
                                                                 PartialOrderType.MORE_PRECISE_THAN,
                                                                 job2.job.configuration[option_under_investigation])},
                                             job1, job2, differences))
        return results
