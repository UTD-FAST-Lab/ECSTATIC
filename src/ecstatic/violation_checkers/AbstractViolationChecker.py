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

import json
import logging
import os.path
import pathlib
import dill as pickle
import time
from abc import ABC, abstractmethod

from pathos.multiprocessing import ProcessPool
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Tuple, Set, Iterable, TypeVar, Optional

import deprecation as deprecation
from pathos.parallel import ParallelPool
from tqdm import tqdm

from src.ecstatic.models.Option import Option
from src.ecstatic.readers.AbstractReader import AbstractReader
from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util.PartialOrder import PartialOrder, PartialOrderType
from src.ecstatic.util.PotentialViolation import PotentialViolation
from src.ecstatic.util.UtilClasses import FinishedFuzzingJob
from src.ecstatic.util.Violation import Violation

logger = logging.getLogger(__name__)
T = TypeVar('T')  # Indicates the type of content in the results (e.g., call graph edges or flows)


def get_file_name(potential_violation: PotentialViolation) -> pathlib.Path:
    filename = Path(*[
        f'{"VIOLATION" if potential_violation.is_violation else "NON-VIOLATION"}',
        f'{"TRANSITIVE" if potential_violation.is_transitive else "DIRECT"}',
        f'{AbstractCommandLineToolRunner.dict_hash(potential_violation.job1.job.configuration)}',
        f'{AbstractCommandLineToolRunner.dict_hash(potential_violation.job2.job.configuration)}',
        f'{potential_violation.get_option_under_investigation().name}',
        *[Path(f'{v.left.level_name}',
               f'{"MST" if v.type == PartialOrderType.MORE_SOUND_THAN else "MPT"}',
               f'{v.right.level_name}') for v in potential_violation.partial_orders],
        f'{os.path.basename(potential_violation.job1.job.target.name)}.json'])
    return filename


def summarize(violations: Iterable[PotentialViolation]):
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


class AbstractViolationChecker(ABC):

    def __init__(self, jobs: int, reader: AbstractReader, output_folder: Path, ground_truths: Optional[Path] = None,
                 write_to_files=True):
        self.output_folder = output_folder
        self.jobs: int = jobs
        self.reader = reader
        self.ground_truths: Path = ground_truths
        self.write_to_files = write_to_files
        logger.debug(f'Ground truths are {self.ground_truths}')

    def check_violations(self, results: List[FinishedFuzzingJob]) -> List[PotentialViolation]:
        start_time = time.time()

        if (pickle_folder := (Path(self.output_folder) / "pickles")).exists():
            finished_results = []
            print("Loading existing violations.")
            for f in tqdm([fil for fil in os.listdir(pickle_folder) if fil.endswith('.pickle')]):
                with open(pickle_folder/f, 'rb') as f:
                    finished_results.append(pickle.load(f))
        else:
            pairs: List[Tuple[FinishedFuzzingJob, FinishedFuzzingJob, Option]] = []
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

            finished_results: List[PotentialViolation] = []
            with ProcessPool(self.jobs) as p:
                print(f'Checking violations with {self.jobs} cores.')
                for result in tqdm(p.imap(self.compare_results, pairs), total=len(pairs)):
                    # Force evaluation of violated
                    # [r for r in result if r.violated]
                    finished_results.extend(result)

            if self.write_to_files:
                def write_violation(violation: PotentialViolation):
                    filename = Path(self.output_folder) / get_file_name(violation)
                    logging.info(f"Filename is {filename}")
                    filename.parent.mkdir(exist_ok=True, parents=True)
                    logging.info(f'Writing violation to file {filename}')
                    with open(filename, 'w') as f:
                        json.dump(violation.as_dict(), f, indent=4)
                    pickle_folder.mkdir(exist_ok=True)
                    with NamedTemporaryFile(dir=pickle_folder, delete=False, suffix='.pickle') as f:
                        pickle.dump(violation, f)

                print("Writing to files.")
                for _ in tqdm(p.imap(write_violation, finished_results), total=len(finished_results)):
                    pass

        print('Violation detection done.')
        print(
            f'Finished checking violations. {len([v for v in finished_results if v.is_violation])} violations detected.')
        print(f'Campaign value processing done (took {time.time() - start_time} seconds).')
        summarize([f for f in finished_results if f.is_violation])
        return finished_results
        # results_queue.task_done()

    @abstractmethod
    def is_true_positive(self, raw_result: T) -> bool:
        pass

    @abstractmethod
    def is_false_positive(self, raw_result: T) -> bool:
        pass

    def get_true_positives(self, raw_results: Iterable[T]) -> Set[T]:
        tps = [t for t in self.read_from_input(self.ground_truths) if self.is_true_positive(t)]
        logger.info(f'{len(tps)} true positives in groundtruths.')
        result = {i for i in raw_results if i in tps}
        logger.info(f'{len(result)} results were true positives.')
        return {i for i in raw_results if i in tps}

    def get_false_positives(self, raw_results: Iterable[T]) -> Set[T]:
        fps = [t for t in self.read_from_input(self.ground_truths) if self.is_false_positive(t)]
        logger.info(f'{len(fps)} false positives in groundtruths.')
        result = {i for i in raw_results if i in fps}
        logger.info(f'{len(result)} results were false positives.')
        return {i for i in raw_results if i in fps}

    def postprocess(self, results: Iterable[T], job: FinishedFuzzingJob) -> Iterable[T]:
        """
        Allows postprocessing of results. By default, does no postprocessing.
        :param results: The results to postprocess.
        :param job: The finished fuzzing job associated with the results.
        :return: The postprocessed result
        """
        return results

    def read_from_input(self, file: Path) -> Iterable[T]:
        return self.reader.import_file(file)

    def compare_results(self, t: Tuple[FinishedFuzzingJob, FinishedFuzzingJob, Option]) -> Iterable[PotentialViolation]:
        """

        Parameters
        ----------
        t: A tuple containing the first job to check, the second job to check, and the option under investigation.

        Returns
        -------

        """
        job1 = t[0]
        job2 = t[1]
        logger.info(f'Job1 is {job1} and job2 is {job2}')
        option_under_investigation = t[2]
        results = []
        if job1.job.configuration[option_under_investigation] == job2.job.configuration[option_under_investigation]:
            return results
        if self.ground_truths is None:
            # In the absence of ground truths, we have to compute violations differently.
            def job1_reader():
                return set(self.postprocess(self.read_from_input(job1.results_location), job1))

            def job2_reader():
                return set(self.postprocess(self.read_from_input(job2.results_location), job2))

            if option_under_investigation.is_more_sound(job1.job.configuration[option_under_investigation],
                                                        job2.job.configuration[option_under_investigation]):
                if option_under_investigation.is_more_precise(job2.job.configuration[option_under_investigation],
                                                              job1.job.configuration[option_under_investigation]):
                    pos: Tuple[PartialOrder, PartialOrder] = \
                        (PartialOrder(job1.job.configuration[option_under_investigation],
                                      PartialOrderType.MORE_SOUND_THAN,
                                      job2.job.configuration[option_under_investigation],
                                      option_under_investigation),
                         PartialOrder(job2.job.configuration[option_under_investigation],
                                      PartialOrderType.MORE_PRECISE_THAN,
                                      job1.job.configuration[option_under_investigation],
                                      option_under_investigation))
                    if pos[0].is_explicit():
                        results.append(PotentialViolation(pos, job1, job2, job1_reader, job2_reader))
                if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                              job2.job.configuration[option_under_investigation]):
                    if option_under_investigation.is_more_sound(job2.job.configuration[option_under_investigation],
                                                                job1.job.configuration[option_under_investigation]):
                        pos = (PartialOrder(job1.job.configuration[option_under_investigation],
                                            PartialOrderType.MORE_PRECISE_THAN,
                                            job2.job.configuration[option_under_investigation],
                                            option_under_investigation),
                               PartialOrder(job2.job.configuration[option_under_investigation],
                                            PartialOrderType.MORE_SOUND_THAN,
                                            job1.job.configuration[option_under_investigation],
                                            option_under_investigation))
                        if pos[0].is_explicit():
                            results.append(PotentialViolation(pos, job1, job2, job1_reader, job2_reader))
        else:
            if option_under_investigation.is_more_sound(job1.job.configuration[option_under_investigation],
                                                        job2.job.configuration[option_under_investigation]):
                def job2_reader():
                    return self.get_true_positives(self.postprocess(self.read_from_input(job2.results_location), job2))

                def job1_reader():
                    return self.get_true_positives(self.postprocess(self.read_from_input(job1.results_location), job1))

                results.append(PotentialViolation(PartialOrder(job1.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_SOUND_THAN,
                                                               job2.job.configuration[option_under_investigation],
                                                               option_under_investigation),
                                                  job1, job2, job1_reader, job2_reader))

            if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                          job2.job.configuration[option_under_investigation]):
                def job2_reader():
                    return self.get_false_positives(self.postprocess(self.read_from_input(job2.results_location), job2))

                def job1_reader():
                    return self.get_false_positives(self.postprocess(self.read_from_input(job1.results_location), job1))

                results.append(PotentialViolation(PartialOrder(job1.job.configuration[option_under_investigation],
                                                               PartialOrderType.MORE_PRECISE_THAN,
                                                               job2.job.configuration[option_under_investigation],
                                                               option_under_investigation),
                                                  job1, job2, job1_reader, job2_reader))
        return results

    @deprecation.deprecated(details="We have passed the functionality of checking for violations to "
                                    "the PotentialViolation object, in order to accomodate the fact that we "
                                    "want to potentially delta debug on non-violations.")
    def check_for_violation(self, t: Tuple[FinishedFuzzingJob, FinishedFuzzingJob, Option]) -> Iterable[Violation]:

        """
        Given two jobs, checks whether there are any violations.
        Parameters
        ----------
        t: A tuple containing the first job to check, the second job to check, and the option under investigation.

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
        if self.ground_truths is None:
            # In the absence of ground truths, we have to compute violations differently.
            if option_under_investigation.is_more_sound(job1.job.configuration[option_under_investigation],
                                                        job2.job.configuration[option_under_investigation]):
                if option_under_investigation.is_more_precise(job2.job.configuration[option_under_investigation],
                                                              job1.job.configuration[option_under_investigation]):
                    # If these are true, and job2 has more stuff than job1, we have a certain violation of one of these
                    # partial orders.
                    job1_input = set(self.postprocess(self.read_from_input(job1.results_location), job1))
                    job2_input = set(self.postprocess(self.read_from_input(job2.results_location), job2))
                    print(f"Job1: {str(job1_input)}, Job2: {str(job2_input)}")
                    differences: Set[T] = job2_input.difference(job1_input)
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
                    results.append(Violation(len(differences) > 0, pos, job1, job2, differences))
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
                job2_result = self.get_true_positives(
                    self.postprocess(self.read_from_input(job2.results_location), job2))
                job1_result = self.get_true_positives(
                    self.postprocess(self.read_from_input(job1.results_location), job1))
                differences = job2_result.difference(job1_result)
                if len(differences) > 0:
                    results.append(Violation(True, {PartialOrder(job1.job.configuration[option_under_investigation],
                                                                 PartialOrderType.MORE_SOUND_THAN,
                                                                 job2.job.configuration[option_under_investigation],
                                                                 option_under_investigation)},
                                             job1, job2, differences))
            if option_under_investigation.is_more_precise(job1.job.configuration[option_under_investigation],
                                                          job2.job.configuration[option_under_investigation]):
                job2_result = self.get_false_positives(
                    self.postprocess(self.read_from_input(job2.results_location), job2))
                job1_result = self.get_false_positives(
                    self.postprocess(self.read_from_input(job1.results_location), job1))
                differences: Set[T] = job1_result.difference(job2_result)
                if len(differences) > 0:
                    results.append(Violation(True, {PartialOrder(job1.job.configuration[option_under_investigation],
                                                                 PartialOrderType.MORE_PRECISE_THAN,
                                                                 job2.job.configuration[option_under_investigation],
                                                                 option_under_investigation)},
                                             job1, job2, differences))

        Path(self.output_folder).mkdir(exist_ok=True, parents=True)
        for violation in filter(lambda v: v.violated, results):
            output_file = get_file_name(violation)
            dirname = os.path.dirname(output_file)
            Path(os.path.join(self.output_folder, "json", dirname)).mkdir(exist_ok=True, parents=True)
            logging.info(f'Writing violation to file {output_file}')
            with open(os.path.join(self.output_folder, "json", output_file), 'w') as f:
                json.dump(violation.as_dict(), f, indent=4)
            with NamedTemporaryFile(dir=self.output_folder, delete=False, suffix='.pickle') as f:
                pickle.dump(violation, f)
