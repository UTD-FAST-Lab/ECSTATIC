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

import logging
import argparse
import importlib
from functools import partial
from pathlib import Path

from src.checkmate.debugging.DeltaDebugger import DeltaDebugger
from src.checkmate.fuzzing.generators import FuzzGeneratorFactory
from src.checkmate.readers import ReaderFactory
from src.checkmate.runners import RunnerFactory
from src.checkmate.util.BenchmarkReader import BenchmarkReader
from src.checkmate.util.Violation import Violation
from src.checkmate.violation_checkers import ViolationCheckerFactory

import subprocess

from src.checkmate.dispatcher import Sanitizer
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker

import os.path
import time
from multiprocessing.pool import Pool
from typing import List
from xml.etree.ElementTree import ElementTree, Element

from src.checkmate.fuzzing.generators.FuzzGenerator import FuzzGenerator
from src.checkmate.models.Flow import Flow
from src.checkmate.models.Option import Option
from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.util import config
from src.checkmate.util.UtilClasses import FuzzingCampaign, FinishedFuzzingJob, FinishedCampaign, Benchmark, \
    BenchmarkRecord

logger = logging.getLogger(__name__)


class ToolTester:

    def __init__(self, generator, runner: AbstractCommandLineToolRunner, debugger: DeltaDebugger | None,
                 results_location: str,
                 num_processes: int, num_campaigns: int, checker: AbstractViolationChecker,
                 limit=None):
        self.generator: FuzzGenerator = generator
        self.runner: AbstractCommandLineToolRunner = runner
        self.debugger: DeltaDebugger = debugger
        self.results_location: str = results_location
        self.unverified_violations = list()
        self.num_processes = num_processes
        self.num_campaigns = num_campaigns
        self.checker = checker
        self.limit = limit

    def main(self):
        campaign_index = 0
        while campaign_index < self.num_campaigns:
            campaign: FuzzingCampaign = self.generator.generate_campaign()
            print(f"Got new fuzzing campaign: {campaign_index}.")
            if campaign_index == 4:
                continue
            start = time.time()

            # Make campaign folder.
            campaign_folder = os.path.join(self.results_location, f'campaign{campaign_index}')
            Path(campaign_folder).mkdir(exist_ok=True, parents=True)
            partial_run_job = partial(self.runner.run_job, output_folder=campaign_folder)
            with Pool(self.num_processes) as p:
                results = list(p.map(partial_run_job,
                                     campaign.jobs if self.limit is None else campaign.jobs[:self.limit - 1]))
            results = [r for r in results if r is not None]
            print(f'Campaign {campaign_index} finished (time {time.time() - start} seconds)')
            violations_folder = os.path.join(campaign_folder, 'violations')
            Path(violations_folder).mkdir(exist_ok=True, parents=True)
            print(f'Now checking for violations.')
            violations: List[Violation] = self.checker.check_violations(results, violations_folder)
            if self.debugger is not None:
                [self.debugger.delta_debug(v) for v in violations]
            self.generator.update_exclusions(violations)
            # self.print_output(FinishedCampaign(results), campaign_index)  # TODO: Replace with generate_report
            print('Done!')
            campaign_index += 1

    def write_flowset(self, relation_type: str,
                      violated: bool,
                      run1: FinishedFuzzingJob,
                      run2: FinishedFuzzingJob,
                      preserve1: List[Flow],
                      preserve2: List[Flow],
                      option_under_investigation: Option,
                      campaign_index: int):
        partial_order = f'{str(run1.job.configuration[option_under_investigation]).split(" ")[0]}_' \
                        f'more_{relation_type}_than_' \
                        f'{str(run2.job.configuration[option_under_investigation]).split(" ")[0]}'
        root = Element('flowset')
        root.set('config1', run1.configuration_location)
        root.set('config2', run2.configuration_location)
        root.set('type', relation_type)
        root.set('partial_order', partial_order)
        root.set('violation', str(violated))

        for j, c in [(run1.configuration_location, preserve1), (run2.configuration_location, preserve2)]:
            preserve = Element('preserve')
            preserve.set('config', j)
            for f in c:
                f: Flow
                preserve.append(f.element)
            root.append(preserve)

        tree = ElementTree(root)
        output_dir = os.path.join(config.configuration['output_directory'],
                                  f"{os.path.basename(run1.configuration_location).split('_')[0]}_"
                                  f"{os.path.basename(run2.configuration_location).split('_')[0]}_"
                                  f"{relation_type}_{partial_order}_campaign{campaign_index}")
        try:
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
        except FileExistsError as fe:
            pass  # silently ignore, we don't care

        output_file = os.path.join(output_dir, f'flowset_violation-{violated}_'
                                               f'{os.path.basename(os.path.dirname(run1.job.target))}_'
                                               f'{os.path.basename(run1.job.target)}.xml')
        tree.write(output_file)
        print(f'Wrote flowset to {os.path.abspath(output_file)}')

    def print_output(self, result: FinishedCampaign, campaign_index: int = 1):
        print('Now processing campaign values.')
        for finished_run in result.finished_jobs:
            finished_run: FinishedFuzzingJob
            option_under_investigation: Option = finished_run.job.option_under_investigation
            # Find configs with potential partial order relationships.
            candidates: List[FinishedFuzzingJob]
            if option_under_investigation is None:
                candidates = [f for f in result.finished_jobs if
                              f.job.target == finished_run.job.target and
                              f.results_location != finished_run.results_location]
            else:
                candidates = [f for f in result.finished_jobs if
                              (f.job.option_under_investigation is None or
                               f.job.option_under_investigation == option_under_investigation) and
                              f.job.target == finished_run.job.target and
                              f.results_location != finished_run.results_location]
            logger.info(f'Found {len(candidates)} candidates for job {finished_run.results_location}')
            for candidate in candidates:
                if finished_run.job.option_under_investigation is None:
                    # switch to the other candidate's
                    option_under_investigation = candidate.job.option_under_investigation
                    if option_under_investigation is None:
                        raise RuntimeError('Trying to compare two configurations with None as the option '
                                           'under investigation. This should never happen.')

                candidate: FinishedFuzzingJob
                if option_under_investigation.is_more_sound(
                        finished_run.job.configuration[option_under_investigation],
                        candidate.job.configuration[
                            option_under_investigation]):  # left side is less sound than right side
                    logger.info(f'{finished_run.job.configuration[option_under_investigation]} is more sound than or '
                                f'equal to {candidate.job.configuration[option_under_investigation]}')
                    violated = len(candidate.detected_flows['tp'].difference(finished_run.detected_flows['tp'])) > 0

                    if violated and self.validate:
                        # Run again to check.
                        print('Verifying violation.')
                        verify = (
                            self.runner.try_run_job(candidate.job, True),
                            self.runner.try_run_job(finished_run.job, True))
                        try:
                            violated = (verify[0].detected_flows['tp'].difference(verify[1].detected_flows['tp'])) == \
                                       (candidate.detected_flows['tp'].difference(finished_run.detected_flows['tp']))
                        except AttributeError:  # in case one of the jobs is None
                            violated = False

                    if violated:
                        logger.info('Detected soundness violation!')
                        preserve_set_1 = list()
                        preserve_set_2 = list(
                            candidate.detected_flows['tp'].difference(finished_run.detected_flows['tp']))
                    else:
                        logger.info('No soundness violation detected.')
                        preserve_set_1 = list(finished_run.detected_flows['tp'])
                        preserve_set_2 = list(candidate.detected_flows['tp'])
                    self.write_flowset(relation_type='soundness', preserve1=preserve_set_1, preserve2=preserve_set_2,
                                       run1=finished_run, run2=candidate, violated=violated,
                                       option_under_investigation=option_under_investigation,
                                       campaign_index=campaign_index)
                if option_under_investigation.is_more_precise(
                        finished_run.job.configuration[option_under_investigation],
                        candidate.job.configuration[
                            option_under_investigation]):  # left side is less precise than right side
                    logger.info(f'{finished_run.job.configuration[option_under_investigation]} is more precise than or '
                                f'equal to {candidate.job.configuration[option_under_investigation]}')
                    violated = len(finished_run.detected_flows['fp'].difference(candidate.detected_flows['fp'])) > 0
                    if violated and self.validate:
                        # Run again to check.
                        print('Verifying violation.')
                        verify = (
                            self.runner.try_run_job(candidate.job, True),
                            self.runner.try_run_job(finished_run.job, True))
                        try:
                            violated = (verify[1].detected_flows['fp'].difference(verify[0].detected_flows['fp'])) == \
                                       (finished_run.detected_flows['fp'].difference(candidate.detected_flows['fp']))
                        except AttributeError:  # in case one of the jobs is None
                            violated = False

                    if violated:
                        logger.info('Precision violation detected!')
                        preserve_set_1 = list(
                            finished_run.detected_flows['fp'].difference(candidate.detected_flows['fp']))
                        preserve_set_2 = list()
                    else:
                        logger.info('No precision violation detected.')
                        preserve_set_1 = list(finished_run.detected_flows['fp'])
                        preserve_set_2 = list(candidate.detected_flows['fp'])
                    self.write_flowset(relation_type='precision', preserve1=preserve_set_1, preserve2=preserve_set_2,
                                       run1=finished_run, run2=candidate, violated=violated,
                                       option_under_investigation=option_under_investigation,
                                       campaign_index=campaign_index)
        print('Campaign value processing done.')
        # results_queue.task_done()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("tool", choices=Sanitizer.tools,
                   help="Tool to run.")
    p.add_argument("benchmark", choices=Sanitizer.benchmarks,
                   help="Benchmark to download and evaluate on.")
    p.add_argument("-t", "--task", choices=Sanitizer.tasks, default="cg",
                   help="Task to run.")
    p.add_argument("-c", "--campaigns", type=int, default=5,
                   help="Number of fuzzing campaigns (i.e., one seed, all of its mutants, and violation detection)")
    p.add_argument("-j", "--jobs", type=int, default=32,
                   help="Number of parallel jobs to do at once.")
    p.add_argument("--adaptive", help="Remove configuration option settings that have already "
                                         "exhibited violations from future fuzzing campaigns.",
                   action="store_true")
    p.add_argument('--timeout', help='Timeout in minutes', type=int)
    p.add_argument('--verbose', '-v', action='count', default=0)
    args = p.parse_args()

    if args.verbose > 1:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    elif args.verbose > 0:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')


    model_location = importlib.resources.path("src.resources.configuration_spaces", f"{args.tool}_config.json")
    grammar = importlib.resources.path("src.resources.grammars", f"{args.tool}_grammar.json")

    benchmark: Benchmark = build_benchmark(args.benchmark)
    logger.info(f'Benchmark is {benchmark}')

    # Check for groundtruths
    tool_dir = importlib.resources.path(f'src.resources.tools.{args.tool}', '')
    files = os.listdir(tool_dir)
    groundtruths = None
    for f in files:
        if args.benchmark.lower() in f.lower() and 'groundtruth' in f.lower():
            groundtruths = os.path.join(tool_dir, f)
            break

    if groundtruths is not None:
        logger.info(f'Using {groundtruths} as groundtruths.')

    results_location = f'/results/{args.tool}/{args.benchmark}'
    Path(results_location).mkdir(exist_ok=True, parents=True)
    runner = RunnerFactory.get_runner_for_tool(args.tool)

    if "dacapo" in args.benchmark.lower():
        runner.whole_program = True
    # Set timeout.
    if args.timeout is not None:
        runner.timeout = args.timeout

    generator = FuzzGeneratorFactory.get_fuzz_generator_for_name(args.tool, model_location, grammar,
                                                                 benchmark, args.adaptive)
    reader = ReaderFactory.get_reader_for_task_and_tool(args.task, args.tool)
    checker = ViolationCheckerFactory.get_violation_checker_for_task(args.task, args.tool,
                                                                     args.jobs, groundtruths, reader)

    Path("/artifacts").mkdir(exist_ok=True)
    debugger = DeltaDebugger("/artifacts", args.tool, args.task, groundtruths)

    t = ToolTester(generator, runner, debugger, results_location,
                   num_processes=args.jobs, num_campaigns=args.campaigns,
                   checker=checker)
    t.main()


def build_benchmark(benchmark: str) -> Benchmark:
    # TODO: Check that benchmarks are loaded. If not, load from git.
    build = importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "build.sh")
    os.chmod(build, 555)
    logging.info(f"Building benchmark....")
    subprocess.run(build)
    if os.path.exists(f'/benchmarks/{benchmark}/index.json'):
        return BenchmarkReader().read_benchmark(f'/benchmarks/{benchmark}/index.json')
    else:
        benchmark_list = []
        for root, dirs, files in os.walk("/benchmarks"):
            benchmark_list.extend([os.path.abspath(os.path.join(root, f)) for f in files if
                                   (f.endswith(".jar") or f.endswith(".apk"))])  # TODO more dynamic extensions?
        return Benchmark([BenchmarkRecord(b) for b in benchmark_list])


if __name__ == '__main__':
    main()
