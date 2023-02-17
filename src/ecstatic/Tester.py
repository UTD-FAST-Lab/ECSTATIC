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
from typing import List, Optional
from enum_actions import enum_action

from tqdm import tqdm

from src.ecstatic.debugging.JavaBenchmarkDeltaDebugger import JavaBenchmarkDeltaDebugger
from src.ecstatic.debugging.JavaViolationDeltaDebugger import JavaViolationDeltaDebugger
from src.ecstatic.fuzzing.generators import FuzzGeneratorFactory
from src.ecstatic.fuzzing.generators.FuzzGenerator import FuzzGenerator, FuzzOptions
from src.ecstatic.readers import ReaderFactory
from src.ecstatic.readers.AbstractReader import AbstractReader
from src.ecstatic.runners import RunnerFactory
from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.util.BenchmarkReader import BenchmarkReader
from src.ecstatic.util.PotentialViolation import PotentialViolation
from src.ecstatic.util.UtilClasses import FuzzingCampaign, Benchmark, \
    BenchmarkRecord, FinishedAnalysisJob
from src.ecstatic.util.Violation import Violation
from src.ecstatic.violation_checkers import ViolationCheckerFactory
from src.ecstatic.violation_checkers.AbstractViolationChecker import AbstractViolationChecker

logger = logging.getLogger(__name__)


class ToolTester:

    def __init__(self,
                 generator,
                 runner: AbstractCommandLineToolRunner,
                 reader: AbstractReader,
                 results_location: str,
                 num_processes: int,
                 num_iterations: int):
        self.generator = generator
        self.runner: AbstractCommandLineToolRunner = runner
        self.results_location: str = results_location
        self.unverified_violations = list()
        self.num_processes = num_processes
        self.num_iterations = num_iterations

    def read_violation_from_file(self, file: str) -> Violation:
        with open(file, 'rb') as f:
            return pickle.load(f)

    def main(self):
        start_time = time.time()
        for campaign_index in range(self.num_iterations):
            campaign, generator_state = self.generator.generate_campaign()
            campaign: FuzzingCampaign
            print(f"Running iteration: {campaign_index}.")
            campaign_start_time = time.time()
            # Make campaign folder.
            campaign_folder = os.path.join(self.results_location, f'iteration{campaign_index}')
            Path(campaign_folder).mkdir(exist_ok=True, parents=True)

            # Run all jobs.
            partial_run_job = partial(self.runner.run_job, output_folder=campaign_folder)
            results: List[FinishedAnalysisJob] = []
            with Pool(self.num_processes) as p:
                for r in tqdm(p.imap(partial_run_job, campaign.jobs), total=len(campaign.jobs)):
                    results.append(r)
            print(f'Iteration {campaign_index} finished (time {time.time() - campaign_start_time} seconds)')
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
    p.add_argument('--timeout', help='Timeout in minutes', type=int)
    p.add_argument('--verbose', '-v', action='count', default=0)
    p.add_argument('--iterations', '-i', type=int, default=1)

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

    generator = FuzzGeneratorFactory.get_fuzz_generator_for_name(args.tool, model_location, benchmark)
    reader = ReaderFactory.get_reader_for_task_and_tool(args.task, args.tool)

    t = ToolTester(generator, runner, reader, results_location, args.jobs, args.iterations)
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
