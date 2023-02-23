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
from datetime import datetime

from tqdm import tqdm
import os
import csv
import shutil

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
        self.reader: AbstractReader = reader
        self.results_location: str = results_location
        self.unverified_violations = list()
        self.num_processes = num_processes
        self.num_iterations = num_iterations

    def read_violation_from_file(self, file: str) -> Violation:
        with open(file, 'rb') as f:
            return pickle.load(f)
        
        
    def move_nd_files(self, file, tool, benchmark):
        output_path = Path('/results') / 'non_determinism' / tool / benchmark
        Path(output_path).mkdir(exist_ok=True, parents=True)
        nd_dir_path_t = os.path.join(output_path, file)
        if not os.path.exists(nd_dir_path_t):
            os.mkdir(nd_dir_path_t)

        for campaign_index in range(self.num_iterations):
            nd_file_path_s = os.path.join(self.results_location, f'iteration{campaign_index}/{file}')
            shutil.copyfile(nd_file_path_s, os.path.join(nd_dir_path_t, f'run_{campaign_index}'))
            
        
    def generate_result_csv(self, results, tool, benchmark):
        header = ['configuration', 'program', 'nondeterminism', 'error']

        output_path = Path('/results') / 'out_csv'
        Path(output_path).mkdir(exist_ok=True, parents=True)
        uuid = datetime.now().strftime('%y%m%dT%H%M%S')
        with open(os.path.join(output_path, f'{tool}_{benchmark}_{uuid}.csv'), 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(results)
                

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

        nd_results = []
        locations = str(self.results_location).rsplit('/', 2)
        tool_name = locations[len(locations) - 2]
        benchmark_name = locations[len(locations) - 1]
        
        match tool_name.lower():
            case "flowdroid":
                for file in os.listdir(os.path.join(self.results_location, 'iteration0')):
                    if file.endswith('.apk.raw'):
                        nd_result_record = [file.split('_', 1)[0], file.rsplit('_', 1)[-1].replace('.apk.raw', '')]
                        file_s = f'{self.results_location}/iteration0/{file}'
                        flows_s = set(self.reader.import_file(file_s)) 
                        nondeterminism = False
                        error = False
                        for campaign_index in range(1, self.num_iterations - 1):
                            if not os.path.exists(f'{self.results_location}/iteration{campaign_index}/{file}'):
                                error = True
                            else:
                                file_t = f'{self.results_location}/iteration{campaign_index}/{file}'
                                flows_t = set(self.reader.import_file(file_t)) 

                                if not flows_s == flows_t:
                                    nondeterminism = True
                                    self.move_nd_files(file, tool_name, benchmark_name)
                                    break

                        nd_result_record.append(nondeterminism)
                        nd_result_record.append(error)
                        nd_results.append(nd_result_record)
            case _:
                pass
        
        self.generate_result_csv(nd_results, tool_name, benchmark_name)
        

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
