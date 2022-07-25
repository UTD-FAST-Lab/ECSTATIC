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
import os
import pathlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

from src.ecstatic.dispatcher import DockerManager


def parse_args():
    tools_dir = importlib.resources.path('src.resources', 'tools')
    benchmarks_dir = importlib.resources.path('src.resources', 'benchmarks')
    parser = argparse.ArgumentParser(description='Just a fuzzing benchmark for static analyzers')
    parser.add_argument('-t',
                        '--tools',
                        help=('static analysis tools to run'
                              'all tools by default'),
                        nargs='+',
                        required=True,
                        choices=list(filter(lambda x: not x.startswith('__'), os.listdir(tools_dir))))
    parser.add_argument('-b',
                        '--benchmarks',
                        help=('benchmark programs to run, incompatible tool and benchmark pairs will be skipped'
                              'all benchmarks by default'),
                        nargs='+',
                        required=True,
                        choices=list(filter(lambda x: not x.startswith('__'), os.listdir(benchmarks_dir))))
    parser.add_argument(
        '--tasks',
        help="Currently a useless option as all tools only support one task. However, this is meant to provide support "
             "for tools that might allow multiple tasks.",
        nargs='+',
        required=True,
        default='cg',
        choices=['cg', 'taint']
    )
    parser.add_argument(
        '--no-cache',
        '-n',
        action='store_true',
        help='Build images without cache'
    )
    parser.add_argument(
        '--jobs',
        '-j',
        help='number of jobs to spawn in each container',
        type=int,
        default='1'
    )
    parser.add_argument(
        '--campaigns',
        '-c',
        help='number of campaigns to run in each container',
        type=int,
        default='1'
    )
    parser.add_argument(
        '--timeout',
        help='The timeout in minutes.',
        type=int
    )
    parser.add_argument(
        '--verbose',
        '-v',
        help="Level of verbosity (more v's gives more output)",
        action='count',
        default=0
    ),
    parser.add_argument(
        '-d', '--delta-debugging-mode',
        choices=['none', 'violation', 'benchmark'],
        default='none'
    )
    parser.add_argument(
        '--fuzzing-timeout',
        help='Time in minutes to allow fuzzing to continue for.',
        type=int,
        default=0
    )
    parser.add_argument(
        '--results-location',
        help='Location to write results.',
        default='./results'
    )
    return parser.parse_args()


def main():
    args = parse_args()

    DockerManager.build_image('base', args.no_cache)
    for t in args.tools:
        DockerManager.build_image(t, args.no_cache)

    for t in args.tools:
        for b in args.benchmarks:
            for task in args.tasks:
                DockerManager.start_runner(t, b, task, args)

if __name__ == '__main__':
    main()
