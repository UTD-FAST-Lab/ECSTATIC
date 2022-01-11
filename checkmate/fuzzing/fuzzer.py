from multiprocessing import JoinableQueue, Process
from typing import List
from functools import partial
import json
from checkmate.fuzzing.FuzzGenerator import FuzzGenerator
from checkmate.fuzzing.FuzzLogger import FuzzLogger
from checkmate.fuzzing.FuzzRunner import FuzzRunner
from checkmate.fuzzing.FuzzScheduler import FuzzScheduler
from ..util import config, FuzzingPairJob


def main(model_location: str, num_processes: int):
    fuzz_job_queue = JoinableQueue(100)
    results_queue = JoinableQueue()

    generator = FuzzGenerator(model_location)
    scheduler = FuzzScheduler(fuzz_job_queue)
    fuzz_logger = FuzzLogger()
    runner = FuzzRunner(config.configuration['apk_location'], fuzz_logger)

    processes = list()

    processes.append(Process(target=partial(fuzz_configurations, generator, scheduler)))
    for i in range(max(num_processes-2, 1)):
        processes.append(Process(target=partial(run_submitted_jobs, scheduler, runner, results_queue)))
    processes.append(Process(target=partial(print_output, results_queue, fuzz_logger)))

    for t in processes:
        t.start()
    #[t.start() for t in processes]
    [t.join() for t in processes]


def fuzz_configurations(generator: FuzzGenerator, scheduler: FuzzScheduler):
    while True:
        for p in generator.get_new_pair():
            scheduler.add_new_job(p)
        #[scheduler.add_new_job(p) for p in generator.get_new_pair()]


def run_submitted_jobs(scheduler: FuzzScheduler, runner: FuzzRunner, results_queue: JoinableQueue):
    while True:
        job: FuzzingPairJob = scheduler.get_next_job_blocking()
        result = runner.run_job(job)
        if result is not None:
            results_queue.put(result)
        scheduler.set_job_as_done()


def print_output(results_queue: JoinableQueue, fuzz_logger: FuzzLogger):
    while True:
        result = results_queue.get()
        with open(config.configuration['results_location'], 'a') as f:
            string_result = json.dumps(result)
            f.write(string_result + '\n')
            print(string_result)
        fuzz_logger.log_new_config(result['config1'], result['apk'])
        fuzz_logger.log_new_config(result['config2'], result['apk'])
        results_queue.task_done()
