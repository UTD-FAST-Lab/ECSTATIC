import dataclasses
from typing import Any

from networkx import DiGraph

from src.checkmate.readers.callgraph.CallGraphReader import CallGraphReader
from src.checkmate.transformers.callgraphs import CallgraphTransformations
from src.checkmate.util.FuzzingJob import FuzzingJob
from src.checkmate.util.UtilClasses import Violation, FinishedFuzzingJob
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker


class CallgraphViolationChecker(AbstractViolationChecker):
    def is_more_precise(self, job1: FinishedFuzzingJob, job2: FinishedFuzzingJob) -> Violation:
        result1 = self.read_from_input(job1.results_location)
        result2 = self.read_from_input(job2.results_location)
        adj1 = CallgraphTransformations.call_site_to_targets(result1)
        adj2 = CallgraphTransformations.call_site_to_targets(result2)
        all_differences = list()
        for k, v in adj1.items():
            if k not in adj2:
                all_differences.extend([f'{k} -> {v1}' for v1 in v])
            else:
                differences = adj2[k] - v
                if len(differences) > 0:
                    all_differences.extend([f'{k} -> {v1}' for v1 in differences])
        job1.job = job1.job.as_dict() if isinstance(job1.job, FuzzingJob) else job1.job
        job2.job = job2.job.as_dict() if isinstance(job2.job, FuzzingJob) else job2.job
        return Violation(len(all_differences) > 0, "precision", dataclasses.asdict(job1), dataclasses.asdict(job2),
                         all_differences)

    def is_more_sound(self, job1: FinishedFuzzingJob, job2: FinishedFuzzingJob) -> Violation:
        result1 = self.read_from_input(job1.results_location)
        result2 = self.read_from_input(job2.results_location)
        adj1 = CallgraphTransformations.call_site_to_targets(result1)
        adj2 = CallgraphTransformations.call_site_to_targets(result2)
        all_differences = list()
        for k, v in adj1.items():
            if k not in adj2:
                all_differences.extend([f'{k} -> {v1}' for v1 in v])
            else:
                differences = v - adj2[k]
                if len(differences) > 0:
                    all_differences.extend([f'{k} -> {v1}' for v1 in differences])
        job1.job = job1.job.as_dict() if isinstance(job1.job, FuzzingJob) else job1.job
        job2.job = job2.job.as_dict() if isinstance(job2.job, FuzzingJob) else job2.job
        return Violation(len(all_differences) > 0, "soundness", dataclasses.asdict(job1), dataclasses.asdict(job2),
                         all_differences)

    def read_from_input(self, file: str) -> DiGraph:
        return CallGraphReader().import_graph(file)
