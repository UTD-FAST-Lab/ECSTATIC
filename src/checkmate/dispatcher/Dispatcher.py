import argparse
import logging
logging.basicConfig(level=logging.DEBUG)

from src.checkmate.dispatcher.Sanitizer import sanity_check, tools, benchmarks, tasks
from src.checkmate.dispatcher import DockerManager

def parse_args():
    parser = argparse.ArgumentParser(description='Just a fuzzing benchmark for static analyzers')
    parser.add_argument('-t',
        '--tools',
        help=('static analysis tools to run'
            'all tools by default'),
        nargs='+',
        required=False,
        default=tools,
        choices=tools)
    parser.add_argument('-b',
        '--benchmarks',
        help=('benchmark programs to run, incompatible tool and benchmark pairs will be skipped'
            'all benchmarks by default'),
        nargs='+',
        required=False,
        default=benchmarks,
        choices=benchmarks)
    parser.add_argument(
        '--tasks',
        help=('tasks to run, incompatible tool and task pairs will be skipped'
            'all tasks by default'),
        nargs='+',
        required=False,
        default=tasks,
        choices=tasks)
    parser.add_argument(
        '--force_build',
        '-f',
        action='store_true',
        help='Force rebuild of image'
    )
    return parser.parse_args()

def main():
    args = parse_args()

    DockerManager.build_image('base')
    for t in args.tools:
        DockerManager.build_image(t, args.force_build)

    for t in args.tools:
        for b in args.benchmarks:
            for task in args.tasks:
                DockerManager.start_runner(t, b, task)

        # comp_benchmarks, comp_tasks = sanity_check(t, args.benchmarks, args.tasks)
        # DockerManager.start_runner(t, args.benchmarks, args.tasks)

if __name__ == '__main__':
    main()





  
