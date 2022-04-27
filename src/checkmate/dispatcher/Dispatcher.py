import argparse
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

from src.checkmate.dispatcher.Sanitizer import sanity_check, tools, benchmarks, tasks
from src.checkmate.dispatcher import DockerManager

def parse_args():
    parser = argparse.ArgumentParser(description='Just a fuzzing benchmark for static analyzers')
    parser.add_argument('-t',
        '--tools',
        help=('static analysis tools to run'
            'all tools by default'),
        nargs='+',
        required=True,
        default=tools,
        choices=tools)
    parser.add_argument('-b',
        '--benchmarks',
        help=('benchmark programs to run, incompatible tool and benchmark pairs will be skipped'
            'all benchmarks by default'),
        nargs='+',
        required=True,
        default=benchmarks,
        choices=benchmarks)
    parser.add_argument(
        '--tasks',
        help=('tasks to run, incompatible tool and task pairs will be skipped'
            'all tasks by default'),
        nargs='+',
        required=True,
        default=tasks,
        choices=tasks)
    parser.add_argument(
        '--nocache',
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
        type=int,
        default='120'
    )
    return parser.parse_args()

def main():
    args = parse_args()

    DockerManager.build_image('base')
    for t in args.tools:
        DockerManager.build_image(t, args.nocache)

    for t in args.tools:
        for b in args.benchmarks:
            for task in args.tasks:
                # TODO: Add sanity check back in
                DockerManager.start_runner(t, b, task, args.jobs, args.campaigns)

        # comp_benchmarks, comp_tasks = sanity_check(t, args.benchmarks, args.tasks)
        # DockerManager.start_runner(t, args.benchmarks, args.tasks)

if __name__ == '__main__':
    main()





  
