import threading
import time
from functools import partial

from checkmate.fuzzing.FuzzGenerator import FuzzGenerator
from checkmate.fuzzing.FuzzRunner import FuzzRunner
from checkmate.fuzzing.FuzzScheduler import FuzzScheduler
from ..util import config


def main(model_location: str, number_configs: int):
    generator = FuzzGenerator(model_location)
    scheduler = FuzzScheduler()
    runner = FuzzRunner(config.configuration['apk_location'])
    fuzzThread = threading.Thread(target=partial(fuzzConfigurations, generator, scheduler))
    runThread = threading.Thread(target=partial(runSubmittedJobs, scheduler, runner))

    current_time = time.time()
    fuzzThread.start()
    runThread.start()

    fuzzThread.join()
    runThread.join()


def fuzzConfigurations(generator: FuzzGenerator, scheduler: FuzzScheduler):
    while True:
        scheduler.addNewJob(generator.getNewPair())

def runSubmittedJobs(scheduler: FuzzScheduler, runner: FuzzRunner):
    while True:
        runner.runJob(scheduler.getNextJobBlocking())

if __name__ == '__main__':
    main()
