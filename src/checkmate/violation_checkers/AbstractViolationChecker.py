#  CheckMate: A Configuration Tester for Static Analysis
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful
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
import shutil
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Tuple, Set, Iterable, TypeVar

from tqdm import tqdm

from src.checkmate.models.Option import Option
from src.checkmate.readers.AbstractReader import AbstractReader
from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.util.PartialOrder import PartialOrder, PartialOrderType
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation

logger = logging.getLogger(__name__)
T = TypeVar('T')  # Indicates the type of content in the results (e.g., call graph edges or flows)


def get_file_name(violation: Violation) -> str:
    filename = f'{"TRANSITIVE" if violation.is_transitive() else "DIRECT"}/'\
               f'{AbstractCommandLineToolRunner.dict_hash(violation.job1.job.configuration)}/' \
               f'{AbstractCommandLineToolRunner.dict_hash(violation.job2.job.configuration)}/' \
               f'{violation.get_option_under_investigation().name}/' + \
               '/'.join([f'{v.left.level_name}/{"MST" if v.type == PartialOrderType.MORE_SOUND_THAN else "MPT"}'
                         f'/{v.right.level_name}' for v in violation.partial_orders]) + \
               f'/{os.path.basename(violation.job1.job.target.name)}.json'
    return filename


@dataclass
class ViolationJob:
    job1: FinishedFuzzingJob
    job2: FinishedFuzzingJob
    output_folder: str
    option_under_investigation: Option
    prior_violations: Iterable[Violation]

class AbstractViolationChecker(ABC):

    def __init__(self, jobs: int, reader: AbstractReader, groundtruths: str | None = None):
        self.jobs: int = jobs
        self.reader = reader
        self.groundtruths = groundtruths
        logger.debug(f'Groundtruths are {self.groundtruths}')

    def check_violations(self, results: Iterable[FinishedFuzzingJob], output_folder: str):
        pairs: Iterable[ViolationJob] = []
        prior_pickles = [os.path.join(output_folder, f) for f in [f1 for f1 in os.listdir(output_folder) if f1.endswith(".pickle")]]
        prior_violations = [pickle.load(open(f, 'rb')) for f in prior_pickles]
        print(f'Found {len(prior_violations)} prior violations.')
        for finished_run in [r for r in results if r is not None]:
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

                pairs.append(ViolationJob(finished_run, candidate, output_folder,
                                          option_under_investigation, prior_violations))

        with Pool(self.jobs) as p:
            print(f'Checking violations with {self.jobs} cores.')
            finished_results = set()
            for result in tqdm(p.imap(self.check_for_violation, pairs), total=len(pairs)):
                finished_results.update(result)
        finished_results = [f for f in finished_results if f.violated]
        self.summarize(finished_results)
        [os.remove(f) for f in prior_pickles]  # Cleanup outdated violations.
        return finished_results

        # print('Violation detection done. Now printing to files.')
        # print('Removing old violations...')
        # shutil.rmtree(output_folder)
        # Path(output_folder).mkdir(exist_ok=False, parents=True)
        # for violation in filter(lambda v: v.violated, finished_results):
        #     filename = get_file_name(violation)
        #     dirname = os.path.dirname(filename)
        #     Path(os.path.join(output_folder, "json", dirname)).mkdir(exist_ok=True, parents=True)
        #     logging.info(f'Writing violation to file {filename}')
        #     with open(os.path.join(output_folder, "json", filename), 'w') as f:
        #         json.dump(violation.as_dict(), f, indent=4)
        #     with NamedTemporaryFile(dir=output_folder, delete=False, suffix='.pickle') as f:
        #         pickle.dump(violation, f)
        # print(f'Finished checking violations. {len([v for v in finished_results if v.violated])} violations detected.')
        # print(f'Campaign value processing done (took {time.time() - start_time} seconds).')
        # self.summarize(finished_results)
        # return finished_results
        # # results_queue.task_done()

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

    def postprocess(self, results: Iterable[T], job: FinishedFuzzingJob) -> Iterable[T]:
        """
        Allows postprocessing of results. By default, does no postprocessing.
        Parameters
        ----------
        results: The results to postprocess.

        Returns
        -------
        The postprocessed result.
        """
        return results

    def read_from_input(self, file: str) -> Iterable[T]:
        return self.reader.import_file(file)

    def check_for_violation(self, violationJob: ViolationJob) -> Iterable[Violation]:

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
        job1 = violationJob.job1
        job2 = violationJob.job2
        option_under_investigation = violationJob.option_under_investigation
        output_folder = violationJob.output_folder
        existing_violations = violationJob.prior_violations
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

                    # Before we read in, check that the violation does not already exist.
                    # This optimization is possible because we don't consider the content of violations
                    # When we check equality.
                    pos: Set[PartialOrder] = {PartialOrder(job1.job.configuration[option_under_investigation],
                                                           PartialOrderType.MORE_SOUND_THAN,
                                                           job2.job.configuration[option_under_investigation],
                                                           option_under_investigation),
                                              PartialOrder(job2.job.configuration[option_under_investigation],
                                                           PartialOrderType.MORE_PRECISE_THAN,
                                                           job1.job.configuration[option_under_investigation],
                                                           option_under_investigation)}
                    v = self.check_violation_job_in_violations_list(violationJob, pos, existing_violations)
                    if v is not None:
                        results.append(v)
                    else:
                        job1_input = set(self.postprocess(self.read_from_input(job1.results_location), job1))
                        job2_input = set(self.postprocess(self.read_from_input(job2.results_location), job2))
                        differences: Set[T] = job2_input.difference(job1_input)
                        results.append(Violation(len(differences), pos, job1, job2, differences))
            if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                          job2.job.configuration[option_under_investigation]):
                if option_under_investigation.is_more_sound(job2.job.configuration[option_under_investigation],
                                                            job1.job.configuration[option_under_investigation]):
                    pos: Set[PartialOrder] = {PartialOrder(job1.job.configuration[option_under_investigation],
                                                           PartialOrderType.MORE_PRECISE_THAN,
                                                           job2.job.configuration[option_under_investigation],
                                                           option_under_investigation),
                                              PartialOrder(job2.job.configuration[option_under_investigation],
                                                           PartialOrderType.MORE_SOUND_THAN,
                                                           job1.job.configuration[option_under_investigation],
                                                           option_under_investigation)}
                    v = self.check_violation_job_in_violations_list(violationJob, pos, existing_violations)
                    if v is not None:
                        results.append(v)
                    else:
                        job1_input = set(self.postprocess(self.read_from_input(job1.results_location), job1))
                        job2_input = set(self.postprocess(self.read_from_input(job2.results_location), job2))
                        differences: Set[T] = job1_input.difference(job2_input)
                        results.append(Violation(len(differences) > 0, pos, job1, job2, differences))
        else:
            if option_under_investigation.is_more_sound(job1.job.configuration[option_under_investigation],
                                                        job2.job.configuration[option_under_investigation]):
                pos = {PartialOrder(job1.job.configuration[option_under_investigation],
                                                                 PartialOrderType.MORE_SOUND_THAN,
                                                                 job2.job.configuration[option_under_investigation],
                                                                 option_under_investigation)}
                v = self.check_violation_job_in_violations_list(violationJob, pos, existing_violations)
                if v is not None:
                    results.append(v)
                else:
                    job2_result = self.get_true_positives(self.postprocess(self.read_from_input(job2.results_location),job2))
                    job1_result = self.get_true_positives(self.postprocess(self.read_from_input(job1.results_location),job1))
                    differences = job2_result.difference(job1_result)
                    results.append(Violation(len(differences) > 0, pos, job1, job2, differences))
            if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                          job2.job.configuration[option_under_investigation]):
                pos = {PartialOrder(job1.job.configuration[option_under_investigation],
                              PartialOrderType.MORE_PRECISE_THAN,
                              job2.job.configuration[option_under_investigation],
                              option_under_investigation)}
                v = self.check_violation_job_in_violations_list(violationJob, pos, existing_violations)
                if v is not None:
                    results.append(v)
                else:
                    job2_result = self.get_false_positives(self.postprocess(self.read_from_input(job2.results_location),job2))
                    job1_result = self.get_false_positives(self.postprocess(self.read_from_input(job1.results_location),job1))
                    differences: Set[T] = job1_result.difference(job2_result)
                    results.append(Violation(len(differences) > 0, pos, job1, job2, differences))

        for violation in results:
            filename = get_file_name(violation)
            dirname = os.path.dirname(filename)
            Path(os.path.join(output_folder, "json", dirname)).mkdir(exist_ok=True, parents=True)
            logging.info(f'Writing violation to file {filename}')
            if violation.violated:
                with open(os.path.join(output_folder, "json", filename), 'w') as f:
                    json.dump(violation.as_dict(), f, indent=4)
            with NamedTemporaryFile(dir=output_folder, delete=False, suffix='.pickle') as f:
                pickle.dump(violation, f)
        return results

    def check_violation_job_in_violations_list(self, violation_job: ViolationJob,
                                               pos: Iterable[PartialOrder],
                                               violations_list: Iterable[Violation]):
        true_violation = Violation(True, pos, violation_job.job1, violation_job.job1, [])
        if true_violation in violations_list:
            return [v for v in violations_list if v == true_violation][0]
        false_violation = Violation(False, pos, violation_job.job1, violation_job.job1, [])
        if false_violation in violations_list:
            return [v for v in violations_list if v == false_violation][0]
        return None

