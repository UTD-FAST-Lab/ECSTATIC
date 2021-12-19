import threading
import time
from functools import partial

from checkmate.fuzzing.FuzzGenerator import FuzzGenerator
from checkmate.fuzzing.FuzzRunner import FuzzRunner
from checkmate.fuzzing.FuzzScheduler import FuzzScheduler
from ..util import config


def main(model_location: str, num_run_threads: int):
    generator = FuzzGenerator(model_location)
    scheduler = FuzzScheduler()
    runner = FuzzRunner(config.configuration['apk_location'])
    threads = list()
    threads.append(threading.Thread(target=partial(fuzzConfigurations, generator, scheduler)))
    for i in range(num_run_threads):
        threads.append(threading.Thread(target=partial(runSubmittedJobs, scheduler, runner)))

    [t.start() for t in threads]
    [t.join() for t in threads]

def fuzzConfigurations(generator: FuzzGenerator, scheduler: FuzzScheduler):
    while True:
        scheduler.addNewJob(generator.getNewPair())

def runSubmittedJobs(scheduler: FuzzScheduler, runner: FuzzRunner):
    while True:
        runner.runJob(scheduler.getNextJobBlocking())

if __name__ == '__main__':
    main()
