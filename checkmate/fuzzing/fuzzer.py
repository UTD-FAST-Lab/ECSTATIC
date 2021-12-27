import threading
from typing import List
from functools import partial

from checkmate.fuzzing.FuzzGenerator import FuzzGenerator
from checkmate.fuzzing.FuzzLogger import FuzzLogger
from checkmate.fuzzing.FuzzRunner import FuzzRunner
from checkmate.fuzzing.FuzzScheduler import FuzzScheduler
from ..util import config


def main(model_location: str, num_run_threads: int):
    generator = FuzzGenerator(model_location)
    scheduler = FuzzScheduler()
    fuzzlogger = FuzzLogger()
    runner = FuzzRunner(config.configuration['apk_location'], fuzzlogger)
    results = list()
    threads = list()

    while True:
        scheduler.addNewJob(generator.getNewPair())
        results.append(runner.runJob(scheduler.getNextJobBlocking()))

    threads.append(threading.Thread(target=partial(fuzzConfigurations, generator, scheduler)))
    for i in range(num_run_threads):
        threads.append(threading.Thread(target=partial(runSubmittedJobs, scheduler, runner, results)))
    threads.append(threading.Thread(target=partial(printOutput, results)))

    [t.start() for t in threads]
    [t.join() for t in threads]


def fuzzConfigurations(generator: FuzzGenerator, scheduler: FuzzScheduler):
    while True:
        scheduler.addNewJob(generator.getNewPair())


def runSubmittedJobs(scheduler: FuzzScheduler, runner: FuzzRunner, results_list: List[str]):
    while True:
        results_list.append(runner.runJob(scheduler.getNextJobBlocking()))


def printOutput(results):
    while True:
        if len(results) > 0:
            print(results.pop(0))


if __name__ == '__main__':
    main()
