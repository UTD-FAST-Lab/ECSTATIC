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

import argparse
import importlib
import logging
import os.path
import pickle
import subprocess
import time
from functools import partial
from multiprocessing.pool import Pool
from pathlib import Path
from typing import List, Optional

from src.checkmate.debugging.DeltaDebugger import DeltaDebugger
from src.checkmate.dispatcher import Sanitizer
from src.checkmate.fuzzing.generators import FuzzGeneratorFactory
from src.checkmate.fuzzing.generators.FuzzGenerator import FuzzGenerator
from src.checkmate.readers import ReaderFactory
from src.checkmate.runners import RunnerFactory
from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.util.BenchmarkReader import BenchmarkReader
from src.checkmate.util.UtilClasses import FuzzingCampaign, Benchmark, \
    BenchmarkRecord
from src.checkmate.util.Violation import Violation
from src.checkmate.violation_checkers import ViolationCheckerFactory
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker

logger = logging.getLogger(__name__)


class ToolTester:

    def __init__(self, generator, runner: AbstractCommandLineToolRunner, debugger: Optional[DeltaDebugger],
                 results_location: str,
                 num_processes: int, num_campaigns: int, checker: AbstractViolationChecker,
                 limit: Optional[int] = None):
        """

        Parameters
        ----------
        limit : object
        """
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
            print(f'Now checking for violations.')
            if os.path.exists(violations_folder):
                logging.warning(f"{violations_folder} exists, so reading existing pickled violations. Please remove "
                                f"{violations_folder} if you want violations to be regenerated.")
                violations: List[Violation] = [pickle.load(open(os.path.join(violations_folder, f), 'rb')) for f in
                                               [f1 for f1 in os.listdir(violations_folder) if f1.endswith('.pickle')]]
            else:
                # Path(violations_folder).mkdir(exist_ok=True, parents=True)
                Path(violations_folder).mkdir(exist_ok=True)
                violations: List[Violation] = self.checker.check_violations(results, violations_folder)
            if self.debugger is not None:
                delta_debugging_folder = os.path.join(campaign_folder, 'deltadebugging')
                Path(delta_debugging_folder).mkdir(exist_ok=True)
                [self.debugger.delta_debug(v, delta_debugging_folder) for v in violations]
            self.generator.update_exclusions(violations)
            # self.print_output(FinishedCampaign(results), campaign_index)  # TODO: Replace with generate_report
            print('Done!')
            campaign_index += 1


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
    p.add_argument('--no-delta-debug', help='Do not delta debug.', action='store_true')
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

    if not args.no_delta_debug:
        Path("/artifacts").mkdir(exist_ok=True)
        debugger = DeltaDebugger("/artifacts", args.tool, args.task, groundtruths)
    else:
        debugger = None

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
    if os.path.exists(importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "index.json")):
        return BenchmarkReader().read_benchmark(importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "index.json"))
    else:
        benchmark_list = []
        for root, dirs, files in os.walk("/benchmarks"):
            benchmark_list.extend([os.path.abspath(os.path.join(root, f)) for f in files if
                                   (f.endswith(".jar") or f.endswith(".apk"))])  # TODO more dynamic extensions?
        return Benchmark([BenchmarkRecord(b) for b in benchmark_list])


if __name__ == '__main__':
    main()
