import copy
import tempfile
from typing import List, Iterable

from hypothesis import strategies, given, assume
from hypothesis.strategies import composite, data

from src.ecstatic.models.Option import Option
from src.ecstatic.readers.SimpleLineReader import SimpleLineReader
from src.ecstatic.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphReader
from src.ecstatic.util.PartialOrder import PartialOrderType
from src.ecstatic.util.PotentialViolation import PotentialViolation
from src.ecstatic.util.UtilClasses import FuzzingJob, FinishedFuzzingJob, BenchmarkRecord
from src.ecstatic.violation_checkers.CallgraphViolationChecker import CallgraphViolationChecker
from tests.strategies.CustomStrategies import callgraph_generator, violation_generator, option_generator


@given(data())
def test_same_callgraph_no_violations(data):
    callgraph = data.draw(callgraph_generator())
    violations = data.draw(violation_generator(callgraph1=callgraph, callgraph2=callgraph))
    assert (len(list(filter(lambda v: v.is_violation, violations))) == 0)

@given(data())
def test_different_callgraph_soundness_violation(data):
    callgraph = data.draw(callgraph_generator(min_callgraph_size=2))
    callgraph1: List[str] = copy.deepcopy(callgraph)
    callgraph2: List[str] = copy.deepcopy(callgraph)
    callgraph1.pop()
    assume(set(callgraph1) != set(callgraph2))
    violations = data.draw(violation_generator(callgraph1=callgraph1, callgraph2=callgraph2,
                                               option=option_generator(partial_order_type=strategies.just(PartialOrderType.MORE_SOUND_THAN))))
    true_violations = list(filter(lambda v: v.is_violation, violations))
    assert(len(true_violations) == 1)

@given(data())
def test_different_callgraph_precision_violation(data):
    callgraph = data.draw(callgraph_generator(min_callgraph_size=2))
    callgraph1: List[str] = copy.deepcopy(callgraph)
    callgraph2: List[str] = copy.deepcopy(callgraph)
    callgraph2.pop()
    assume(set(callgraph1) != set(callgraph2))
    violations = data.draw(violation_generator(callgraph1=callgraph1, callgraph2=callgraph2,
                                               option=option_generator(partial_order_type=strategies.just(PartialOrderType.MORE_PRECISE_THAN))))
    true_violations = list(filter(lambda v: v.is_violation and v.get_main_partial_order().is_explicit(), violations))
    assert(len(true_violations) == 1)