import argparse
import importlib
import logging
logging.basicConfig(level=logging.DEBUG)
import os.path
import time
from multiprocessing.pool import Pool
from typing import List
from xml.etree.ElementTree import ElementTree, Element

from src.checkmate.fuzzing.FuzzGenerator import FuzzGenerator
from src.checkmate.models.Flow import Flow
from src.checkmate.models.Option import Option
from src.checkmate.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.checkmate.runners.DOOPRunner import DOOPRunner
from src.checkmate.runners.SOOTRunner import SOOTRunner
from src.checkmate.runners.WALARunner import WALARunner
from src.checkmate.util import config
from src.checkmate.util.UtilClasses import FuzzingCampaign, FinishedFuzzingJob, FinishedCampaign

logger = logging.getLogger(__name__)


class ToolTester:

    def __init__(self, generator, runner: AbstractCommandLineToolRunner,
                 num_processes: int, num_campaigns: int, validate: bool):
        self.generator = generator
        self.runner = runner
        self.unverified_violations = list()
        self.num_processes = num_processes
        self.num_campaigns = num_campaigns
        self.validate = validate

    def main(self):
        campaign_index = 0

        while campaign_index < self.num_campaigns:
            campaign_index += 1
            campaign: FuzzingCampaign = self.generator.generate_campaign()
            print(f"Got new fuzzing campaign: {campaign_index}.")
            if campaign_index == 4:
                continue
            start = time.time()
            with Pool(self.num_processes) as p:
                results = list(p.map(self.runner.run_job, campaign.jobs))
            results = [r for r in results if r is not None]
            print(f'Campaign {campaign_index} finished (time {time.time() - start} seconds)')
            #self.print_output(FinishedCampaign(results), campaign_index)  # TODO: Replace with generate_report
            print('Done!')

    def write_flowset(self, relation_type: str,
                      violated: bool,
                      run1: FinishedFuzzingJob,
                      run2: FinishedFuzzingJob,
                      preserve1: List[Flow],
                      preserve2: List[Flow],
                      option_under_investigation: Option,
                      campaign_index: int):
        partial_order = f'{str(run1.job.configuration[option_under_investigation]).split(" ")[0]}_' \
                        f'more_{relation_type}_than_' \
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

    def print_output(self, result: FinishedCampaign, campaign_index: int = 1):
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
                if option_under_investigation.is_more_sound(
                        finished_run.job.configuration[option_under_investigation],
                        candidate.job.configuration[
                            option_under_investigation]):  # left side is less sound than right side
                    logger.info(f'{finished_run.job.configuration[option_under_investigation]} is more sound than or '
                                f'equal to {candidate.job.configuration[option_under_investigation]}')
                    violated = len(candidate.detected_flows['tp'].difference(finished_run.detected_flows['tp'])) > 0

                    if violated and self.validate:
                        # Run again to check.
                        print('Verifying violation.')
                        verify = (self.runner.run_job(candidate.job, True), self.runner.run_job(finished_run.job, True))
                        try:
                            violated = (verify[0].detected_flows['tp'].difference(verify[1].detected_flows['tp'])) == \
                                       (candidate.detected_flows['tp'].difference(finished_run.detected_flows['tp']))
                        except AttributeError:  # in case one of the jobs is None
                            violated = False

                    if violated:
                        logger.info('Detected soundness violation!')
                        preserve_set_1 = list()
                        preserve_set_2 = list(
                            candidate.detected_flows['tp'].difference(finished_run.detected_flows['tp']))
                    else:
                        logger.info('No soundness violation detected.')
                        preserve_set_1 = list(finished_run.detected_flows['tp'])
                        preserve_set_2 = list(candidate.detected_flows['tp'])
                    self.write_flowset(relation_type='soundness', preserve1=preserve_set_1, preserve2=preserve_set_2,
                                       run1=finished_run, run2=candidate, violated=violated,
                                       option_under_investigation=option_under_investigation,
                                       campaign_index=campaign_index)
                if option_under_investigation.is_more_precise(
                        finished_run.job.configuration[option_under_investigation],
                        candidate.job.configuration[
                            option_under_investigation]):  # left side is less precise than right side
                    logger.info(f'{finished_run.job.configuration[option_under_investigation]} is more precise than or '
                                f'equal to {candidate.job.configuration[option_under_investigation]}')
                    violated = len(finished_run.detected_flows['fp'].difference(candidate.detected_flows['fp'])) > 0
                    if violated and self.validate:
                        # Run again to check.
                        print('Verifying violation.')
                        verify = (self.runner.run_job(candidate.job, True), self.runner.run_job(finished_run.job, True))
                        try:
                            violated = (verify[1].detected_flows['fp'].difference(verify[0].detected_flows['fp'])) == \
                                       (finished_run.detected_flows['fp'].difference(candidate.detected_flows['fp']))
                        except AttributeError:  # in case one of the jobs is None
                            violated = False

                    if violated:
                        logger.info('Precision violation detected!')
                        preserve_set_1 = list(
                            finished_run.detected_flows['fp'].difference(candidate.detected_flows['fp']))
                        preserve_set_2 = list()
                    else:
                        logger.info('No precision violation detected.')
                        preserve_set_1 = list(finished_run.detected_flows['fp'])
                        preserve_set_2 = list(candidate.detected_flows['fp'])
                    self.write_flowset(relation_type='precision', preserve1=preserve_set_1, preserve2=preserve_set_2,
                                       run1=finished_run, run2=candidate, violated=violated,
                                       option_under_investigation=option_under_investigation,
                                       campaign_index=campaign_index)
        print('Campaign value processing done.')
        # results_queue.task_done()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("tool", choices=["soot","doop","wala"])
    p.add_argument("benchmarks", choices=["dacapo","droidbench","sample"])
    p.add_argument("-t", "--task", choices=["cg"], default="cg")
    p.add_argument("-c", "--campaigns", type=int, default=1)
    p.add_argument("-j", "--jobs", type=int, default=1)
    args = p.parse_args()

    model_location = importlib.resources.path("src.resources.configuration_spaces", f"{args.tool}_config.json")
    grammar = importlib.resources.path("src.resources.grammars",f"{args.tool}_grammar.json")

    if args.tool == "soot":
        runner = SOOTRunner()
    elif args.tool == "wala":
        runner = WALARunner()
    else:
        runner = DOOPRunner()

    t = ToolTester(FuzzGenerator(model_location, grammar, "/checkmate/benchmarks/"), runner,
                   num_processes=args.jobs, num_campaigns=args.campaigns, validate=False)
    t.main()


if __name__ == '__main__':
    main()
