import os.path
from multiprocessing import JoinableQueue, Process
from functools import partial
import logging
import json
from multiprocessing.pool import Pool
from typing import List
from xml.etree.ElementTree import ElementTree

from checkmate.fuzzing.FuzzGenerator import FuzzGenerator
from checkmate.fuzzing.FuzzRunner import FuzzRunner
from checkmate.fuzzing.FuzzScheduler import FuzzScheduler
from ..models.Flow import Flow
from ..models.Option import Option
from ..util import config, FuzzingJob
from ..util.NamedTuples import FuzzingCampaign, FinishedFuzzingJob, FinishedCampaign

logger = logging.getLogger(__name__)


def main(model_location: str, num_processes: int):
    fuzz_job_queue = JoinableQueue(100)
    results_queue = JoinableQueue()

    generator = FuzzGenerator(model_location)
    scheduler = FuzzScheduler(fuzz_job_queue)
    runner = FuzzRunner(config.configuration['apk_location'])

    processes = list()

    processes.append(Process(target=partial(fuzz_configurations, generator, scheduler)))
    processes.append(Process(target=partial(run_submitted_jobs, scheduler, runner, results_queue)))
    processes.append(Process(target=partial(print_output, results_queue)))

    for t in processes:
        t.start()

    [t.join() for t in processes]


def fuzz_configurations(generator: FuzzGenerator, scheduler: FuzzScheduler):
    while True:
        logger.info("Generating new fuzzing campaign.")
        scheduler.add_new_job(generator.generate_campaign())
        logger.info("New fuzzing campaign generated.")


def run_submitted_jobs(scheduler: FuzzScheduler, runner: FuzzRunner, results_queue: JoinableQueue):
    while True:
        try:
            campaign: FuzzingCampaign = scheduler.get_next_job_blocking()
            campaign_result: List[FuzzingJob] = list()
            logger.info(f"Starting fuzzing campaign with {len(campaign.jobs)}")
            with Pool() as p:
                results = p.map(runner.run_job, campaign.jobs)
            campaign_results = list(filter(lambda x: x is not None, results))
            logger.info("Finished fuzzing campaign.")
            results_queue.put(FinishedCampaign(campaign_results))
            scheduler.set_job_as_done()
        except Exception as ex:
            logger.exception('Run failed')


def write_flowset(relation_type: str,
                  violated: bool,
                  run1: FinishedFuzzingJob,
                  run2: FinishedFuzzingJob, preserve1: List[Flow],
                  preserve2: List[Flow]):
    root = ElementTree.Element('flowset')
    root.set('config1', run1.configuration_location)
    root.set('config2', run2.configuration_location)
    root.set('type', relation_type)
    root.set('partial_order',
             f'{run1.job.option_under_investigation}={run1.job.configuration[run1.job.option_under_investigation]} '
             f'less {relation_type} than '
             f'{run2.job.option_under_investigation}={run2.job.configuration[run2.job.option_under_investigation]}')
    root.set('violation', str(violated))

    for j, c in [(run1.configuration_location, preserve1), (run2.configuration_location, preserve2)]:
        preserve = ElementTree.Element('preserve')
        preserve.set('config', j)
        for f in c:
            f: Flow
            preserve.append(f.element)
        root.append(preserve)

    tree = ElementTree.ElementTree(root)
    output_dir = os.path.join(config.configuration['output_directory'],
                              f"{os.path.basename(run1.configuration_location.replace('.xml', ''))}_"
                              f"{os.path.basename(run2.configuration_location.replace('.xml', ''))}_"
                              f"{relation_type}")

    try:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
    except FileExistsError as fe:
        pass  # silently ignore, we don't care

    output_file = os.path.join(output_dir, f'flowset_violation-{violated}_{os.path.basename(run1.job.apk)}.xml')
    tree.write(output_file)
    print(f'Output result to {os.path.basename(output_file)}')


def print_output(results_queue: JoinableQueue):
    while True:
        result: FinishedCampaign = results_queue.get()
        for finished_run in result.finished_jobs:
            finished_run: FinishedFuzzingJob
            option_under_investigation: Option = finished_run.job.option_under_investigation
            # Find configs with potential partial order relationships.
            candidates: List[FinishedFuzzingJob]
            if option_under_investigation is None:
                candidates = result.finished_jobs
            else:
                candidates = [f for f in result.finished_jobs if
                              (f.job.option_under_investigation is None or
                               f.job.option_under_investigation == option_under_investigation) and
                              f.job.apk == finished_run.job.apk]

            for candidate in candidates:
                candidate: FinishedFuzzingJob
                # check if there is a partial order relationship
                soundness_level = option_under_investigation.soundness_compare(
                    finished_run.job.configuration[option_under_investigation],
                    candidate.job.configuration[option_under_investigation])
                precision_level = option_under_investigation.precision_compare(
                    finished_run.job.configuration[option_under_investigation],
                    candidate.job.configuration[option_under_investigation])
                if soundness_level < 0:  # left side is less sound than right side
                    violated = len(finished_run.detected_flows['tp'].difference(candidate.detected_flows['tp'])) > 0
                    if violated:
                        preserve_set_1 = list(
                            finished_run.detected_flows['tp'].difference(candidate.detected_flows['tp']))
                        preserve_set_2 = list()
                    else:
                        preserve_set_1 = list(finished_run.detected_flows['tp'])
                        preserve_set_2 = list(candidate.detected_flows['tp'])
                    write_flowset(relation_type='soundness', preserve1=preserve_set_1, preserve2=preserve_set_2,
                                  run1=finished_run, run2=candidate)
                if precision_level < 0:  # left side is less precise than right side
                    violated = len(candidate.detected_flows['fp'].difference(finished_run.detected_flows['fp'])) > 0
                    if violated:
                        preserve_set_1 = list()
                        preserve_set_2 = list(candidate.detected_flows['fp'].difference(finished_run.detected_flows['fp']))
                    else:
                        preserve_set_1 = list(finished_run.detected_flows['fp'])
                        preserve_set_2 = list(candidate.detected_flows['fp'])
                    write_flowset(relation_type='precision', preserve1=preserve_set_1, preserve2=preserve_set_2,
                                  run1=finished_run, run2=candidate)

        results_queue.task_done()
