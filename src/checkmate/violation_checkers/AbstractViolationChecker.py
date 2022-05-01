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

import json
import logging
import os.path
import pickle
import time
from abc import ABC, abstractmethod
from multiprocessing import Pool
from tempfile import NamedTemporaryFile
from typing import List, Any, Tuple, Set, Iterable, TypeVar

from src.checkmate.models.Option import Option
from src.checkmate.readers.AbstractReader import AbstractReader
from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.util.PartialOrder import PartialOrder, PartialOrderType
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation

logger = logging.getLogger(__name__)
T = TypeVar('T')  # Indicates the type of content in the results (e.g., call graph edges or flows)


def get_file_name(violation: Violation) -> str:
    filename = f'violation_{AbstractCommandLineToolRunner.dict_hash(violation.job1.job.configuration)}_' \
               f'{AbstractCommandLineToolRunner.dict_hash(violation.job2.job.configuration)}_' \
               f'{violation.get_option_under_investigation().name}_' \
               f'{"_".join(violation.partial_orders)}' \
               f'{os.path.basename(violation.job1.job.target.name)}.json'
    return filename


class AbstractViolationChecker(ABC):

    def __init__(self, jobs: int, reader: AbstractReader, groundtruths: str | None = None):
        self.jobs: int = jobs
        self.reader = reader
        self.groundtruths = groundtruths
        logger.debug(f'Groundtruths are {self.groundtruths}')

    def check_violations(self, results: Iterable[FinishedFuzzingJob], output_folder: str,
                         finished_results: Iterable[Violation] = []) -> List[Violation]:
        start_time = time.time()
        pairs: Iterable[Tuple[FinishedFuzzingJob, FinishedFuzzingJob, Option]] = {}
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

                pairs.add((finished_run, candidate, option_under_investigation))

        already_checked_pairs = {(v.job1, v.job2, v.get_option_under_investigation()) for v in finished_results}
        if len(already_checked_pairs.difference(pairs)) > 0:
            for job1, job2, op in already_checked_pairs.difference(pairs):
                logger.critical(f'Found a violation between {job1.results_location} and {job2.results_location} on '
                                f'option {op} that is out-of-date or otherwise erroneously included.')
        pairs = pairs.difference(already_checked_pairs)
        with Pool(self.jobs) as p:
            print(f'Checking violations with {self.jobs} cores.')
            [finished_results.extend(v_set) for v_set in p.starmap(self.check_for_violation, pairs)]

        for violation in filter(lambda v: v.violated, finished_results):
            filename = get_file_name(violation)
            with open(os.path.join(output_folder, filename), 'w') as f:
                json.dump(violation.as_dict(), f, indent=4)
            with NamedTemporaryFile(dir=output_folder, delete=False, suffix='.pickle') as f:
                pickle.dump(violation, f)
        print(f'Finished checking violations. {len([v for v in finished_results if v.violated])} violations detected.')
        print(f'Campaign value processing done (took {time.time() - start_time} seconds).')
        self.summarize(finished_results)
        return finished_results
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
        print("------------------------")
        print("Option (Number of Violations)")
        for k in keys:
            print(f'{k} ({summary_struct[k]})')

    @abstractmethod
    def is_true_positive(self, input: T) -> bool:
        pass

    @abstractmethod
    def is_false_positive(self, input: T) -> bool:
        pass

    def get_true_positives(self, input: Iterable[T]) -> Set[T]:
        tps = [t for t in self.read_from_input(self.groundtruths) if self.is_true_positive(t)]
        logger.info(f'{len(tps)} true positives in groundtruths.')
        result = {i for i in input if i in tps}
        logger.info(f'Out of {len(input)} flows, {len(result)} were true positives.')
        return {i for i in input if i in tps}

    def get_false_positives(self, input: Iterable[T]) -> Set[T]:
        fps = [t for t in self.read_from_input(self.groundtruths) if self.is_false_positive(t)]
        logger.info(f'{len(fps)} false positives in groundtruths.')
        result = {i for i in input if i in fps}
        logger.info(f'Out of {len(input)} flows, {len(result)} were true positives.')
        return {i for i in input if i in fps}

    def read_from_input(self, file: str) -> Iterable[T]:
        return self.reader.import_file(file)

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
        if job1.job.configuration[option_under_investigation] == job2.job.configuration[option_under_investigation]:
            return results
        if self.groundtruths is None:
            # In the absence of ground truths, we have to compute violations differently.
            if option_under_investigation.is_more_sound(job1.job.configuration[option_under_investigation],
                                                        job2.job.configuration[option_under_investigation]):
                if option_under_investigation.is_more_precise(job2.job.configuration[option_under_investigation],
                                                              job1.job.configuration[option_under_investigation]):
                    # If these are true, and job2 has more stuff than job1, we have a certain violation of one of these
                    # partial orders.
                    job1_input = set(self.read_from_input(job1.results_location))
                    job2_input = set(self.read_from_input(job2.results_location))

                    differences: Set[T] = job2_input.difference(job1_input)
                    if len(differences) > 0:
                        logger.info(f'Found {len(differences)} differences between '
                                    f'{job2.results_location} ({len(job2_input)}) and '
                                    f'{job1.results_location} ({len(job1_input)})')
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
                    job1_input = set(self.read_from_input(job1.results_location))
                    job2_input = set(self.read_from_input(job2.results_location))
                    differences: Set[T] = job1_input.difference(job2_input)

                    differences: Set[T] = set(self.read_from_input(job1.results_location)).difference(
                        set(self.read_from_input(job2.results_location)))
                    if len(differences) > 0:
                        logger.info(f'Found {len(differences)} differences between '
                                    f'{job2.results_location} ({len(job2_input)}) and '
                                    f'{job1.results_location} ({len(job1_input)})')
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
