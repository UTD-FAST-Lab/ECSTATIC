import argparse
import logging

from Sanitizer import sanity_check, tools, benchmarks, tasks
import DockerManager

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
        '--build',
        help='(re)build base images and tool runners',
        action='store_true',
        required=False)
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

    if args.build:
        for t in args.tools:
            DockerManager.build_image('base')
            DockerManager.build_image(t)

    if not DockerManager.check_image('base'):
        DockerManager.build_image('base')
    for t in args.tools:
        if not DockerManager.check_image(t):
            DockerManager.build_image(t)

        comp_benchmarks, comp_tasks = sanity_check(t, args.benchmarks, args.tasks)

        DockerManager.start_runner(t, comp_benchmarks, comp_tasks)

if __name__ == '__main__':
    main()





  
