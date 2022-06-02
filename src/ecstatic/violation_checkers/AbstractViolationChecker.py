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

#  CheckMate: A Configuration Tester for Static Analysis
#
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
import sys
import time
from abc import ABC, abstractmethod
from multiprocessing import Pool
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Any, Tuple, Set, Iterable, TypeVar

from tqdm import tqdm

from src.ecstatic.models.Option import Option
from src.ecstatic.readers.AbstractReader import AbstractReader
from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util.PartialOrder import PartialOrder, PartialOrderType
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob
from src.ecstatic.util.Violation import Violation

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


class AbstractViolationChecker(ABC):

    def __init__(self, jobs: int, reader: AbstractReader, groundtruths: str | None = None):
        self.output_folder = None
        self.jobs: int = jobs
        self.reader = reader
        self.groundtruths = groundtruths
        logger.debug(f'Groundtruths are {self.groundtruths}')

    def check_violations(self, results: Iterable[FinishedFuzzingJob], output_folder: str,
                         finished_results: Iterable[Violation] = []) -> List[Violation]:
        self.output_folder = output_folder
        start_time = time.time()
        if len(finished_results) == 0:
            pairs: Set[Tuple[FinishedFuzzingJob, FinishedFuzzingJob, Option]] = []
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

                    logging.info(f"Added pair {str(finished_run)} {str(candidate)} {str(option_under_investigation)})")
                    pairs.append((finished_run, candidate, option_under_investigation))

            with Pool(self.jobs) as p:
                print(f'Checking violations with {self.jobs} cores.')
                for result in tqdm(p.imap(self.check_for_violation, pairs), total=len(pairs)):
                    pass

        print('Violation detection done.')
        print('Now reading them back in.')
        finished_results = set([pickle.load(open(os.path.join(output_folder, f), 'rb'))
                                for f in os.listdir(self.output_folder) if f.endswith('.pickle')])
        vfile = open(os.path.join(output_folder,"violations_text"),'w')
        finalstr="";
        for x in finished_results:
            if x.violated:
                finalstr+=str(x.as_dict())
        vfile.write(finalstr);
        vfile.flush()
        vfile.close()
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

    def check_for_violation(self, t: Tuple[FinishedFuzzingJob, FinishedFuzzingJob, Option]):

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
        job1 = t[0]
        job2 = t[1]
        logger.info(f'Job1 is {job1} and job2 is {job2}')
        option_under_investigation = t[2]
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
                    job1_input = set(self.postprocess(self.read_from_input(job1.results_location), job1))
                    job2_input = set(self.postprocess(self.read_from_input(job2.results_location), job2))
                    differences: Set[T] = job2_input.difference(job1_input)
                    if len(differences) > 0:
                        logger.info(f'Found {len(differences)} differences between '
                                    f'{job2.results_location} ({len(job2_input)}) and '
                                    f'{job1.results_location} ({len(job1_input)})')
                        pos: Set[PartialOrder] = {PartialOrder(job1.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_SOUND_THAN,
                                                               job2.job.configuration[option_under_investigation],
                                                               option_under_investigation),
                                                  PartialOrder(job2.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_PRECISE_THAN,
                                                               job1.job.configuration[option_under_investigation],
                                                               option_under_investigation)}
                        results.append(Violation(True, pos, job1, job2, differences))
                    del job1_input
                    del job2_input
            if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                          job2.job.configuration[option_under_investigation]):
                if option_under_investigation.is_more_sound(job2.job.configuration[option_under_investigation],
                                                            job1.job.configuration[option_under_investigation]):
                    job1_input = set(self.postprocess(self.read_from_input(job1.results_location), job1))
                    job2_input = set(self.postprocess(self.read_from_input(job2.results_location), job2))
                    differences: Set[T] = job1_input.difference(job2_input)
                    if len(differences) > 0:
                        logger.info(f'Found {len(differences)} differences between '
                                    f'{job2.results_location} ({len(job2_input)}) and '
                                    f'{job1.results_location} ({len(job1_input)})')
                        pos: Set[PartialOrder] = {PartialOrder(job1.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_PRECISE_THAN,
                                                               job2.job.configuration[option_under_investigation],
                                                               option_under_investigation),
                                                  PartialOrder(job2.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_SOUND_THAN,
                                                               job1.job.configuration[option_under_investigation],
                                                               option_under_investigation)}
                        results.append(Violation(True, pos, job1, job2, differences))
                        del job1_input
                        del job2_input
        else:
            if option_under_investigation.is_more_sound(job1.job.configuration[option_under_investigation],
                                                        job2.job.configuration[option_under_investigation]):
                job2_result = self.get_true_positives(self.postprocess(self.read_from_input(job2.results_location),job2))
                job1_result = self.get_true_positives(self.postprocess(self.read_from_input(job1.results_location),job1))
                differences = job2_result.difference(job1_result)
                if len(differences) > 0:
                    results.append(Violation(True, {PartialOrder(job1.job.configuration[option_under_investigation],
                                                                 PartialOrderType.MORE_SOUND_THAN,
                                                                 job2.job.configuration[option_under_investigation],
                                                                 option_under_investigation)},
                                             job1, job2, differences))
            if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                          job2.job.configuration[option_under_investigation]):
                job2_result = self.get_false_positives(self.postprocess(self.read_from_input(job2.results_location),job2))
                job1_result = self.get_false_positives(self.postprocess(self.read_from_input(job1.results_location),job1))
                differences: Set[T] = job1_result.difference(job2_result)
                if len(differences) > 0:
                    results.append(Violation(True, {PartialOrder(job1.job.configuration[option_under_investigation],
                                                                 PartialOrderType.MORE_PRECISE_THAN,
                                                                 job2.job.configuration[option_under_investigation],
                                                                 option_under_investigation)},
                                             job1, job2, differences))

        Path(self.output_folder).mkdir(exist_ok=True, parents=True)
        for violation in filter(lambda v: v.violated, results):
            filename = get_file_name(violation)
            dirname = os.path.dirname(filename)
            Path(os.path.join(self.output_folder, "json", dirname)).mkdir(exist_ok=True, parents=True)
            logging.info(f'Writing violation to file {filename}')
            with open(os.path.join(self.output_folder, "json", filename), 'w') as f:
                json.dump(violation.as_dict(), f, indent=4)
            with NamedTemporaryFile(dir=self.output_folder, delete=False, suffix='.pickle') as f:
                pickle.dump(violation, f)


