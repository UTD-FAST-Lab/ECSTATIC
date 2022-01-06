import threading
from typing import List
from functools import partial
import json
from checkmate.fuzzing.FuzzGenerator import FuzzGenerator
from checkmate.fuzzing.FuzzLogger import FuzzLogger
from checkmate.fuzzing.FuzzRunner import FuzzRunner
from checkmate.fuzzing.FuzzScheduler import FuzzScheduler
from ..util import config


def main(model_location: str, num_run_threads: int):
    generator = FuzzGenerator(model_location)
    scheduler = FuzzScheduler()
    fuzz_logger = FuzzLogger()
    runner = FuzzRunner(config.configuration['apk_location'], fuzz_logger)
    results = list()
    threads = list()

    threads.append(threading.Thread(target=partial(fuzz_configurations, generator, scheduler)))
    for i in range(num_run_threads):
        threads.append(threading.Thread(target=partial(run_submitted_jobs, scheduler, runner, results)))
    threads.append(threading.Thread(target=partial(print_output, results)))

    [t.start() for t in threads]
    [t.join() for t in threads]


def fuzz_configurations(generator: FuzzGenerator, scheduler: FuzzScheduler):
    while True:
        scheduler.add_new_job(generator.get_new_pair())


def run_submitted_jobs(scheduler: FuzzScheduler, runner: FuzzRunner, results_list: List[str]):
    while True:
        [results_list.append(r) for r in runner.run_job(scheduler.get_next_job_blocking())]


def print_output(results):
    while True:
        if len(results) > 0:
            with open(config.configuration['results_location'], 'a') as  f:
                result = results.pop(0)
                string_result = json.dumps(result)
                f.write(string_result)
                print(string_result)
