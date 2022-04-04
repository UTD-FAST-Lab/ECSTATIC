from networkx import DiGraph

from src.checkmate.readers.callgraph.CallGraphReader import CallGraphReader
from src.checkmate.transformers.callgraphs import CallgraphTransformations
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker


class CallgraphViolationChecker(AbstractViolationChecker):
    def is_more_precise(self, job1: FinishedFuzzingJob, job2: FinishedFuzzingJob) -> Violation:
        result1 = self.read_from_input(job1.results_location)
        result2 = self.read_from_input(job2.results_location)
        adj1 = CallgraphTransformations.call_site_to_targets(result1)
        adj2 = CallgraphTransformations.call_site_to_targets(result2)
        all_differences = list()
        for k, v in adj1.items():
            """
            For each call site, if job1 is more precise than job2, we expect job1's
            targets to be a subset of job2's. So violations are anything in
            job1 - job2
            
            If we have a callsite in adj1 that is not in adj2, then all of its
            sites are violations.
            """
            if k in adj2:
                all_differences.extend([f'{k} -> {v1}' for v1 in v.difference(
                    (adj2[k] if k in adj2 else set()))])
        return Violation(len(all_differences) > 0, "precision", job1, job2, all_differences)

    def is_more_sound(self, job1: FinishedFuzzingJob, job2: FinishedFuzzingJob) -> Violation:
        result1 = self.read_from_input(job1.results_location)
        result2 = self.read_from_input(job2.results_location)
        adj1 = CallgraphTransformations.call_site_to_targets(result1)
        adj2 = CallgraphTransformations.call_site_to_targets(result2)
        all_differences = list()
        for k, v in adj2.items():
            """
            For each call site, if job1 is more sound than job2, then we expect
            job2's targets to be a subset of job1's. Thus, a violation is anything in
            job2 - job1.
            
            If there is a callsite in adj2 that is not in adj1, then all of the out-edges
            are a violation.
            """
            if k in adj1:
                all_differences.extend([f'{k} -> {v1}' for v1 in v.difference(
                    (adj1[k] if k in adj1 else set()))])
        return Violation(len(all_differences) > 0, "soundness", job1, job2, all_differences)

    def read_from_input(self, file: str) -> DiGraph:
        return CallGraphReader().import_graph(file)
