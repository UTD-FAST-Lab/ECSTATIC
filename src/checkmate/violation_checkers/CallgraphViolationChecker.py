import json
import os.path
from typing import Dict

from networkx import DiGraph

from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.checkmate.transformers.callgraphs import CallgraphTransformations
from src.checkmate.util.CGCallSite import CGCallSite
from src.checkmate.util.CGTarget import CGTarget
from src.checkmate.util.UtilClasses import FinishedFuzzingJob
from src.checkmate.util.Violation import Violation
from src.checkmate.violation_checkers.AbstractViolationChecker import AbstractViolationChecker


class CallgraphViolationChecker(AbstractViolationChecker):

    def __init__(self, output: str, reader: AbstractCallGraphReader):
        self.reader = reader
        super().__init__(output)

    def is_more_precise(self, job1: FinishedFuzzingJob, job2: FinishedFuzzingJob) -> Violation:
        result1 = self.read_from_input(job1.results_location)
        result2 = self.read_from_input(job2.results_location)
        all_differences = list()
        for k, v in result1.items():
            """
            For each call site, if job1 is more precise than job2, we expect job1's
            targets to be a subset of job2's. So violations are anything in
            job1 - job2
            
            If we have a callsite in adj1 that is not in adj2, then all of its
            sites are violations.
            """
            if k in result2:
                all_differences.extend([f'{k} -> {v1}' for v1 in v.difference(
                    (result2[k] if k in result2 else set()))])
        return Violation(len(all_differences) > 0, "precision", job1, job2, all_differences)

    def is_more_sound(self, job1: FinishedFuzzingJob, job2: FinishedFuzzingJob) -> Violation:
        result1 = self.read_from_input(job1.results_location)
        result2 = self.read_from_input(job2.results_location)
        all_differences = list()
        for k, v in result2.items():
            """
            For each call site, if job1 is more sound than job2, then we expect
            job2's targets to be a subset of job1's. Thus, a violation is anything in
            job2 - job1.
            
            If there is a callsite in adj2 that is not in adj1, then all of the out-edges
            are a violation.
            """
            if k in result1:
                all_differences.extend([f'{k} -> {v1}' for v1 in v.difference(
                    (result1[k] if k in result2 else set()))])
        return Violation(len(all_differences) > 0, "soundness", job1, job2, all_differences)

    def read_from_input(self, file: str) -> Dict[CGCallSite, CGTarget]:
        if os.path.exists(file.replace('.raw', '.cg.json')):
            with open(file.replace('.raw', '.cg.json')) as f:
                return {CGCallSite(**k): [CGTarget(**v1) for v1 in v] for k, v in json.load(f)}
        else:
            callgraph: Dict[CGCallSite, CGTarget] = self.reader.import_graph(file)
            with open(file.replace('.raw', '.cg.json'), 'w') as f:
                json.dump(callgraph, f, default=lambda x: x.__dict__)
