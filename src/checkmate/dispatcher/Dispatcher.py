import argparse
import logging

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
        required=False,
        default=tasks,
        choices=tasks)
    return parser.parse_args()

def main():
    args = parse_args()

    DockerManager.build_image('base')
    for t in args.tools:
        DockerManager.build_image(t)

    for t in args.tools:
        comp_benchmarks, comp_tasks = sanity_check(t, args.benchmarks, args.tasks)

        DockerManager.start_runner(t, comp_benchmarks, comp_tasks)

if __name__ == '__main__':
    main()





  
