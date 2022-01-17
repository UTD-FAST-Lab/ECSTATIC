import os.path
import time
from multiprocessing import JoinableQueue, Process
from functools import partial
import logging
import json
from multiprocessing.pool import Pool
from typing import List
from xml.etree.ElementTree import ElementTree, Element

import tqdm as tqdm

from checkmate.fuzzing.FuzzGenerator import FuzzGenerator
from checkmate.fuzzing.FuzzRunner import FuzzRunner
from checkmate.fuzzing.FuzzScheduler import FuzzScheduler
from ..models.Flow import Flow
from ..models.Option import Option
from ..util import config, FuzzingJob
from ..util.NamedTuples import FuzzingCampaign, FinishedFuzzingJob, FinishedCampaign

logger = logging.getLogger(__name__)


def main(model_location: str, num_processes: int, num_campaigns: int):
    generator = FuzzGenerator(model_location)
    runner = FuzzRunner(config.configuration['apk_location'])

    campaign_index = 0

    while campaign_index < num_campaigns:
        campaign_index += 1
        campaign: FuzzingCampaign = generator.generate_campaign()
        start = time.time()
        with Pool(num_processes) as p:
            results = list(p.map(runner.run_job, campaign.jobs))
        print(f'Campaign {campaign_index} finished (time {time.time() - start} seconds)')
        print_output(FinishedCampaign(results), campaign_index)
        print('Done!')


def fuzz_configurations(generator: FuzzGenerator, scheduler: FuzzScheduler):
    while True:
        logger.info("Generating new fuzzing campaign.")
        scheduler.add_new_job(generator.generate_campaign())
        logger.info("New fuzzing campaign generated.")


def run_submitted_jobs(scheduler: FuzzScheduler, runner: FuzzRunner, results_queue: JoinableQueue, num_processes: int):
    while True:
        try:
            campaign: FuzzingCampaign = scheduler.get_next_job_blocking()
            campaign_result: List[FuzzingJob] = list()
            print(f"Starting fuzzing campaign with {len(campaign.jobs)}")
            with Pool(max(1, num_processes-2)) as p: # -2 because of the other two processes we spawn (parent and the generator)
                results = list(p.imap_unordered(runner.run_job, campaign.jobs, chunksize=100))
            campaign_results = list(filter(lambda x: x is not None, results))
            print("Finished fuzzing campaign.")
            results_queue.put(FinishedCampaign(campaign_results))
            scheduler.set_job_as_done()
        except Exception as ex:
            logger.exception('Run failed')


def write_flowset(relation_type: str,
                  violated: bool,
                  run1: FinishedFuzzingJob,
                  run2: FinishedFuzzingJob,
                  preserve1: List[Flow],
                  preserve2: List[Flow],
                  option_under_investigation: Option,
                  campaign_index: int):
    partial_order = f'{str(run1.job.configuration[option_under_investigation]).split(" ")[0]}_'\
             f'more_{relation_type}_than_'\
             f'{str(run2.job.configuration[option_under_investigation]).split(" ")[0]}'
    root = Element('flowset')
    root.set('config1', run1.configuration_location)
    root.set('config2', run2.configuration_location)
    root.set('type', relation_type)
    root.set('partial_order', partial_order)
    root.set('violation', str(violated))

    for j, c in [(run1.configuration_location, preserve1), (run2.configuration_location, preserve2)]:
        preserve = Element('preserve')
        preserve.set('config', j)
        for f in c:
            f: Flow
            preserve.append(f.element)
        root.append(preserve)

    tree = ElementTree(root)
    output_dir = os.path.join(config.configuration['output_directory'],
                              f"{os.path.basename(run1.configuration_location).split('_')[0]}_"
                              f"{os.path.basename(run2.configuration_location).split('_')[0]}_"
                              f"{relation_type}_{partial_order}_campaign{campaign_index}")
    try:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
    except FileExistsError as fe:
        pass  # silently ignore, we don't care

    output_file = os.path.join(output_dir, f'flowset_violation-{violated}_'
                                           f'{os.path.basename(os.path.dirname(run1.job.apk))}_'
                                           f'{os.path.basename(run1.job.apk)}.xml')
    tree.write(output_file)
    print(f'Wrote flowset to {os.path.abspath(output_file)}')


def print_output(result: FinishedCampaign, campaign_index: int = 1):
    print('Now processing campaign values.')
    for finished_run in result.finished_jobs:
        finished_run: FinishedFuzzingJob
        option_under_investigation: Option = finished_run.job.option_under_investigation
        # Find configs with potential partial order relationships.
        candidates: List[FinishedFuzzingJob]
        if option_under_investigation is None:
            candidates = [f for f in result.finished_jobs if
            f.job.apk == finished_run.job.apk and
            f.results_location != finished_run.results_location]
        else:
            candidates = [f for f in result.finished_jobs if
                          (f.job.option_under_investigation is None or
                           f.job.option_under_investigation == option_under_investigation) and
                          f.job.apk == finished_run.job.apk and
                          f.results_location != finished_run.results_location]
        logger.info(f'Found {len(candidates)} candidates for job {finished_run.results_location}')
        for candidate in candidates:
            if finished_run.job.option_under_investigation is None:
                # switch to the other candidate's
                option_under_investigation = candidate.job.option_under_investigation
                if option_under_investigation is None:
                    raise RuntimeError('Trying to compare two configurations with None as the option '
                                       'under investigation. This should never happen.')

            candidate: FinishedFuzzingJob
            # check if there is a partial order relationship
            # logger.info(f'Soundness level between {finished_run.job.configuration[option_under_investigation]} and'
            #             f'{candidate.job.configuration[option_under_investigation]} is {soundness_level}')
            # precision_level = option_under_investigation.precision_compare(
            #     finished_run.job.configuration[option_under_investigation],
            #     candidate.job.configuration[option_under_investigation])
            # logger.info(f'Precision level between {finished_run.job.configuration[option_under_investigation]} and'
            #             f'{candidate.job.configuration[option_under_investigation]} is {precision_level}')
            if option_under_investigation.is_more_sound(
                finished_run.job.configuration[option_under_investigation],
                candidate.job.configuration[option_under_investigation]): # left side is less sound than right side
                logger.info(f'{finished_run.job.configuration[option_under_investigation]} is more sound than or '
                            f'equal to {candidate.job.configuration[option_under_investigation]}')
                violated = len(candidate.detected_flows['tp'].difference(finished_run.detected_flows['tp'])) > 0
                if violated:
                    logger.info('Detected soundness violation!')
                    preserve_set_1 = list()
                    preserve_set_2 = list(candidate.detected_flows['tp'].difference(finished_run.detected_flows['tp']))
                else:
                    logger.info('No soundness violation detected.')
                    preserve_set_1 = list(finished_run.detected_flows['tp'])
                    preserve_set_2 = list(candidate.detected_flows['tp'])
                write_flowset(relation_type='soundness', preserve1=preserve_set_1, preserve2=preserve_set_2,
                              run1=finished_run, run2=candidate, violated=violated,
                              option_under_investigation=option_under_investigation, campaign_index=campaign_index)
            if option_under_investigation.is_more_precise(
                finished_run.job.configuration[option_under_investigation],
                candidate.job.configuration[option_under_investigation]):  # left side is less precise than right side
                logger.info(f'{finished_run.job.configuration[option_under_investigation]} is more precise than or '
                            f'equal to {candidate.job.configuration[option_under_investigation]}')
                violated = len(finished_run.detected_flows['fp'].difference(candidate.detected_flows['fp'])) > 0
                if violated:
                    logger.info('Precision violation detected!')
                    preserve_set_1 = list(finished_run.detected_flows['fp'].difference(candidate.detected_flows['fp']))
                    preserve_set_2 = list()
                else:
                    logger.info('No precision violation detected.')
                    preserve_set_1 = list(finished_run.detected_flows['fp'])
                    preserve_set_2 = list(candidate.detected_flows['fp'])
                write_flowset(relation_type='precision', preserve1=preserve_set_1, preserve2=preserve_set_2,
                              run1=finished_run, run2=candidate, violated=violated,
                              option_under_investigation=option_under_investigation, campaign_index=campaign_index)
    print('Campaign value processing done.')
        #results_queue.task_done()
