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
import logging
import os.path
import pickle
import subprocess
import time
from functools import partial
from multiprocessing.pool import Pool
from pathlib import Path
from typing import List, Optional

from tqdm import tqdm

from src.ecstatic.debugging.DeltaDebugger import DeltaDebugger
from src.ecstatic.dispatcher import Sanitizer
from src.ecstatic.fuzzing.generators import FuzzGeneratorFactory
from src.ecstatic.fuzzing.generators.FuzzGenerator import FuzzGenerator
from src.ecstatic.readers import ReaderFactory
from src.ecstatic.runners import RunnerFactory
from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.toolreverter.BinarySearch import BinarySearch
from src.ecstatic.toolreverter.Reverter import ReverterFactory, Reverter
from src.ecstatic.util.BenchmarkReader import BenchmarkReader
from src.ecstatic.util.UtilClasses import FuzzingCampaign, Benchmark, \
    BenchmarkRecord
from src.ecstatic.util.Violation import Violation
from src.ecstatic.violation_checkers import ViolationCheckerFactory
from src.ecstatic.violation_checkers.AbstractViolationChecker import AbstractViolationChecker

logger = logging.getLogger(__name__)


class ToolTester:

    def __init__(self, generator, runner: AbstractCommandLineToolRunner, debugger: Optional[DeltaDebugger],
                 results_location: str,
                 num_processes: int, fuzzing_timeout: int, checker: AbstractViolationChecker,
                 reverter: Reverter):
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
        self.fuzzing_timeout = fuzzing_timeout
        self.checker = checker
        self.reverter = reverter;

    def read_violation_from_file(self, file: str) -> Violation:
        with open(file, 'rb') as f:
            return pickle.load(f)

    def main(self):
        campaign_index = 0
        start_time = time.time()
        while True:
            campaign: FuzzingCampaign = self.generator.generate_campaign()
            print(f"Got new fuzzing campaign: {campaign_index}.")
            campaign_start_time = time.time()
            # Make campaign folder.
            campaign_folder = os.path.join(self.results_location, f'campaign{campaign_index}')
            Path(campaign_folder).mkdir(exist_ok=True, parents=True)
            partial_run_job = partial(self.runner.run_job, output_folder=campaign_folder)
            with Pool(self.num_processes) as p:
                results = []
                for r in tqdm(p.imap(partial_run_job, campaign.jobs), total=len(campaign.jobs)):
                    results.append(r)
            results = [r for r in results if r is not None and r.results_location is not None]
            print(f'Campaign {campaign_index} finished (time {time.time() - campaign_start_time} seconds)')
            violations_folder = os.path.join(campaign_folder, 'violations')
            print(f'Now checking for violations.')
            existing_violations = []
            if os.path.exists(violations_folder):
                logging.warning(f"{violations_folder} exists, so reading existing pickled violations. Please remove "
                                f"{violations_folder} if you want violations to be recomputed.")
                with Pool(self.num_processes) as p:
                    existing_violations = p.map(self.read_violation_from_file,
                                                [os.path.join(violations_folder, v) for v in
                                                 os.listdir(violations_folder) if v.endswith('.pickle')])
                logging.info(f'Read in {len(existing_violations)} existing violations.')
            Path(violations_folder).mkdir(exist_ok=True)
            violations: List[Violation] = self.checker.check_violations(results, violations_folder, existing_violations)

            # Perform binary search on things

            search = BinarySearch(self.reverter.GITREPO, self.reverter.FROM_TAG, self.reverter.TO_TAG, violations,
                                  self.runner, self.reverter,checker=self.checker)
            search_results = search.performsearch();
            with open("/results/search_results.txt", 'w') as f:
                for x in search_results:
                    f.write(str(x) + "\n");

            if self.debugger is not None:
                with Pool(max(int(self.num_processes / 2),
                              1)) as p:  # /2 because each delta debugging process needs 2 cores.
                    direct_violations = [v for v in violations if not v.is_transitive()]
                    print(f'Delta debugging {len(direct_violations)} violations with {self.num_processes} cores.')
                    p.map(partial(self.debugger.delta_debug, campaign_directory=campaign_folder,
                                  timeout=self.runner.timeout), direct_violations)
            self.generator.feedback(violations)
            print(f'Done with campaign {campaign_index}!')
            campaign_index += 1
            if time.time() - start_time > self.fuzzing_timeout * 60:
                break
        print('Testing done!')


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
    p.add_argument('--fuzzing-timeout', help='Fuzzing timeout in minutes.', type=int, default=0)
    p.add_argument('--uid', help='If passed, change artifacts to be owned by the user after each step.')
    p.add_argument('--gid', help='If passed, change artifacts to be owned by the user after each step.')
    p.add_argument('--to_tag',
                   help="If passed, enables binary search this project in the range from_tag -> to_tag, requires both to_tag and from_tag to be passed",
                   type=str)
    p.add_argument('--from_tag',
                   help="If passed, enables binary search this project in the range from_tag -> to_tag, requires both to_tag and from_tag to be passed",
                   type=str)
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
                                                                 benchmark)
    reader = ReaderFactory.get_reader_for_task_and_tool(args.task, args.tool)
    checker = ViolationCheckerFactory.get_violation_checker_for_task(args.task, args.tool,
                                                                     args.jobs, groundtruths, reader)

    if args.to_tag is None and args.from_tag is not None:
        print("Please add both to_tag and from_tag");
        exit(0)
    if args.to_tag is not None and args.from_tag is None:
        print("please add both to_tag and from_tag");
        exit(0)
    tool_reverter = ReverterFactory().get_reverter(args.tool.lower(), args.from_tag, args.to_tag);

    if not args.no_delta_debug:
        Path("/artifacts").mkdir(exist_ok=True)
        debugger = DeltaDebugger("/artifacts", args.tool, args.task, groundtruths, runner.whole_program)
    else:
        debugger = None

    t = ToolTester(generator, runner, debugger, results_location,
                   num_processes=args.jobs, fuzzing_timeout=args.fuzzing_timeout,
                   checker=checker, reverter=tool_reverter)
    t.main()


def build_benchmark(benchmark: str) -> Benchmark:
    # TODO: Check that benchmarks are loaded. If not, load from git.
    if not os.path.exists("/benchmarks"):
        build = importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "build.sh")
        os.chmod(build, 555)
        logging.info(f"Building benchmark....")
        subprocess.run(build)
    if os.path.exists(importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "index.json")):
        return BenchmarkReader().read_benchmark(
            importlib.resources.path(f"src.resources.benchmarks.{benchmark}", "index.json"))
    else:
        benchmark_list = []
        for root, dirs, files in os.walk("/benchmarks"):
            benchmark_list.extend([os.path.abspath(os.path.join(root, f)) for f in files if
                                   (f.endswith(".jar") or f.endswith(".apk"))])  # TODO more dynamic extensions?
        return Benchmark([BenchmarkRecord(b) for b in benchmark_list])


if __name__ == '__main__':
    main()
