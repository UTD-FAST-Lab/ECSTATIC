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


import argparse
import importlib
import json
import logging
import os.path
import pickle
import random
import subprocess
import time
from functools import partial
from multiprocessing.dummy import Pool
from pathlib import Path
from typing import Optional, Iterable, List

from enum_actions import enum_action
from tqdm import tqdm

from src.ecstatic.debugging.JavaBenchmarkDeltaDebugger import JavaBenchmarkDeltaDebugger
from src.ecstatic.debugging.JavaViolationDeltaDebugger import JavaViolationDeltaDebugger
from src.ecstatic.debugging.TimeBasedDeltaDebugger import TimeBasedDeltaDebugger
from src.ecstatic.fuzzing.generators import FuzzGeneratorFactory
from src.ecstatic.fuzzing.generators.FuzzGenerator import FuzzGenerator, FuzzOptions
from src.ecstatic.readers import ReaderFactory
from src.ecstatic.runners import RunnerFactory
from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util.BenchmarkReader import BenchmarkReader
from src.ecstatic.util.UtilClasses import FuzzingCampaign, Benchmark, \
    BenchmarkRecord, FinishedFuzzingJob
from src.ecstatic.util.Violation import Violation
from src.ecstatic.violation_checkers import ViolationCheckerFactory
from src.ecstatic.violation_checkers.AbstractViolationChecker import AbstractViolationChecker

logger = logging.getLogger(__name__)


class ToolTester:

    def __init__(self, generator, runner: AbstractCommandLineToolRunner, debugger: Optional[TimeBasedDeltaDebugger],
                 results_location: str,
                 num_processes: int, fuzzing_timeout: int, checker: AbstractViolationChecker,
                 seed: int):
        self.generator: FuzzGenerator = generator
        self.runner: AbstractCommandLineToolRunner = runner
        self.debugger: TimeBasedDeltaDebugger = debugger
        self.results_location: str = results_location
        self.unverified_violations = list()
        self.num_processes = num_processes
        self.fuzzing_timeout = fuzzing_timeout
        self.checker = checker
        self.seed = seed

    def read_violation_from_file(self, file: str) -> Violation:
        with open(file, 'rb') as f:
            return pickle.load(f)

    def main(self):
        campaign_index = 0
        start_time = time.time()
        while True:
            campaign, generator_state = self.generator.generate_campaign()
            campaign: FuzzingCampaign
            print(f"Got new fuzzing campaign: {campaign_index}.")
            campaign_start_time = time.time()
            # Make campaign folder.
            if campaign_index == 0:
                campaign_folder = os.path.join(self.results_location, f'campaign{campaign_index}')
            else:
                campaign_folder = Path(self.results_location) / str(self.seed) / self.generator.strategy.name / \
                                  (f'full_campaign{campaign_index}' if
                                   self.generator.full_campaigns else f'campaign{campaign_index}')
            Path(campaign_folder).mkdir(exist_ok=True, parents=True)

            with open(Path(campaign_folder) / "fuzzer_state.json", 'w') as f:
                json.dump(generator_state, f)

            partial_run_job = partial(self.runner.run_job, output_folder=campaign_folder)
            with Pool(self.num_processes) as p:
                results: List[FinishedFuzzingJob] = []
                for r in tqdm(p.imap(partial_run_job, campaign.jobs), total=len(campaign.jobs)):
                    results.append(r)
            results: Iterable[FinishedFuzzingJob] = [r for r in results if r is not None and r.results_location is not None]
            print(f'Campaign {campaign_index} finished (time {time.time() - campaign_start_time} seconds)')
            # violations_folder = Path(campaign_folder) / 'violations'
            # self.checker.output_folder = violations_folder
            # print(f'Now checking for violations.')
            # Path(violations_folder).mkdir(exist_ok=True)
            # violations: List[PotentialViolation] = self.checker.check_violations(results)
            # print(f"Total potential violations: {len(violations)}")
            to_delta_debug = [r for r in results if r.execution_time_in_ms > self.debugger.maximum_time_in_seconds * 1000]
            logger.info(f"Delta debugging {len(to_delta_debug)} jobs.")
            if self.debugger is not None:
                with Pool(max(int(self.num_processes / 2),
                              1)) as p:  # /2 because each delta debugging process needs 2 cores.
                    p.map(partial(self.debugger.delta_debug, campaign_directory=campaign_folder,
                                  timeout=self.runner.timeout),
                                  (r for r in results if r.execution_time_in_ms > self.debugger.maximum_time_in_seconds * 1000))
            print(f'Done with campaign {campaign_index}!')
            campaign_index += 1
            # if self.uid is not None and self.gid is not None:
            #    logger.info("Changing permissions of folder.")
            #    os.chown(campaign_folder, int(self.uid), int(self.gid))
            #    for root, dirs, files in os.walk(campaign_folder):
            #        files = map(lambda x: os.path.join(root, x), files)
            #        map(lambda x: os.chown(x, int(self.uid), self.gid), files)
            if time.time() - start_time > self.fuzzing_timeout * 60:
                break
        print('Testing done!')


def main():
    p = argparse.ArgumentParser()
    p.add_argument("tool", help="Tool to run.")
    p.add_argument("benchmark", help="Benchmark to download and evaluate on.")
    p.add_argument("-t", "--task", help="Task to run.", default="cg")
    p.add_argument("-c", "--campaigns", type=int, default=5,
                   help="Number of fuzzing campaigns (i.e., one seed, all of its mutants, and violation detection)")
    p.add_argument("-j", "--jobs", type=int, default=32,
                   help="Number of parallel jobs to do at once.")
    p.add_argument("--adaptive", help="Remove configuration option settings that have already "
                                      "exhibited violations from future fuzzing campaigns.",
                   action="store_true")
    p.add_argument('--timeout', help='Timeout in minutes', type=int)
    p.add_argument('--verbose', '-v', action='count', default=0)
    p.add_argument('--fuzzing-timeout', help='Fuzzing timeout in minutes.', type=int, default=0)
    p.add_argument(
        '-d', '--delta-debugging-mode',
        choices=['none', 'violation', 'benchmark'],
        default='none'
    )
    p.add_argument("--seed", help="Seed to use for the random fuzzer", type=int, default=2001)
    p.add_argument("--fuzzing-strategy", action=enum_action(FuzzOptions), default="GUIDED")
    p.add_argument("--full-campaigns", help="Do not sample at all, just do full campaigns.", action='store_true')
    p.add_argument("--hdd-only", help="Disable the delta debugger's CDG phase.", action='store_true')

    args = p.parse_args()

    random.seed(args.seed)

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

    results_location = Path('/results') / args.tool / args.benchmark

    Path(results_location).mkdir(exist_ok=True, parents=True)
    runner = RunnerFactory.get_runner_for_tool(args.tool)

    if "dacapo" in args.benchmark.lower():
        runner.whole_program = True
    # Set timeout.
    if args.timeout is not None:
        runner.timeout = args.timeout

    generator = FuzzGeneratorFactory.get_fuzz_generator_for_name(args.tool, model_location, grammar,
                                                                 benchmark, args.fuzzing_strategy,
                                                                 args.full_campaigns)
    reader = ReaderFactory.get_reader_for_task_and_tool(args.task, args.tool)
    checker = ViolationCheckerFactory.get_violation_checker_for_task(args.task, args.tool,
                                                                     jobs=args.jobs,
                                                                     ground_truths=groundtruths,
                                                                     reader=reader,
                                                                     output_folder=results_location / "violations")

    # match args.delta_debugging_mode.lower():
    #     case 'violation': debugger = JavaViolationDeltaDebugger(runner, reader, checker, hdd_only=args.hdd_only)
    #     case 'benchmark': debugger = JavaBenchmarkDeltaDebugger(runner, reader, checker, hdd_only=args.hdd_only)
    #     case _: debugger = None
    debugger = TimeBasedDeltaDebugger(runner, reader, checker, 5 * 60)

    t = ToolTester(generator, runner, debugger, results_location,
                   num_processes=args.jobs, fuzzing_timeout=args.fuzzing_timeout,
                   checker=checker, seed=args.seed)
    t.main()


def build_benchmark(benchmark: str) -> Benchmark:
    # TODO: Check that benchmarks are loaded. If not, load from git.
    if not os.path.exists("/benchmarks"):
        build = importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "build.sh")
        logging.info(f"Building benchmark....")
        subprocess.run(build)
    if os.path.exists(importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "index.json")):
        return BenchmarkReader().read_benchmark(
            importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "index.json"))
    else:
        benchmark_list = []
        for root, dirs, files in os.walk("/benchmarks"):
            benchmark_list.extend([os.path.abspath(os.path.join(root, f)) for f in files if
                                   (f.endswith(".jar") or f.endswith(".apk") or f.endswith(
                                       ".js"))])  # TODO more dynamic extensions?
        return Benchmark([BenchmarkRecord(b) for b in benchmark_list])


if __name__ == '__main__':
    main()
