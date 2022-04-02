from typing import Any

from networkx import DiGraph

from src.checkmate.readers.callgraph.CallGraphReader import CallGraphReader
from src.checkmate.util.UtilClasses import Violation, FinishedFuzzingJob
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker


class CallgraphViolationChecker(AbstractViolationChecker):
    def is_more_precise(self, job1: FinishedFuzzingJob, job2: FinishedFuzzingJob) -> Violation:
        result1 = self.read_from_input(job1.results_location)
        result2 = self.read_from_input(job2.results_location)
        adj1 = {k: v for k, v in result1.adjacency()}
        adj2 = {k: v for k, v in result2.adjacency()}
        all_differences = list()
        for k, v in adj1.items():
            if k not in adj2:
                all_differences.extend([f'{k} -> {v1.content}' for v1 in v])
            else:
                differences = set(adj2[k]) - set(v)
                if len(differences) > 0:
                    all_differences.extend([f'{k} -> {v1.content}' for v1 in differences])
        return Violation(len(all_differences) > 0, "precision", job1, job2, all_differences)


    def is_more_sound(self, job1: FinishedFuzzingJob, job2: FinishedFuzzingJob) -> Violation:
        result1 = self.read_from_input(job1.results_location)
        result2 = self.read_from_input(job2.results_location)

        adj1 = {k: v for k, v in result1.adjacency()}
        adj2 = {k: v for k, v in result2.adjacency()}
        all_differences = list()
        for k, v in adj1.items():
            if k not in adj2:
                all_differences.extend([f'{k} -> {v1.content}' for v1 in v])
            else:
                differences = set(v) - set(adj2[k])
                if len(differences) > 0:
                    all_differences.extend([f'{k} -> {v1.content}' for v1 in differences])
        return Violation(len(all_differences) > 0, "soundness", job1, job2, all_differences)

    def read_from_input(self, file: str) -> DiGraph:
        return CallGraphReader.import_graph(file)