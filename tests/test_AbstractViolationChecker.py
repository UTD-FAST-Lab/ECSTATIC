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


@composite
def option_generator(draw,
                     option_name=strategies.text(),
                     level1_name=strategies.text(),
                     level2_name=strategies.text(),
                     partial_order_type=strategies.one_of(strategies.just(PartialOrderType.MORE_SOUND_THAN),
                                                          strategies.just(PartialOrderType.MORE_PRECISE_THAN))):
    option: Option = Option(draw(option_name))
    level1 = draw(level1_name)
    level2 = draw(level2_name)
    assume(level1 != level2)
    option.add_level(level1)
    option.add_level(level2)
    match (draw(partial_order_type)):
        case PartialOrderType.MORE_PRECISE_THAN:
            option.set_more_precise_than(level1, level2)
        case PartialOrderType.MORE_SOUND_THAN:
            option.set_more_sound_than(level1, level2)
    return option


@composite
def callgraph_generator(draw,
                        line_generator=strategies.from_regex(r"(?:[^\t\n]+?\t){4}(?:[^\t\n]+)"),
                        min_callgraph_size=1):
    return draw(strategies.lists(line_generator, min_size=min_callgraph_size))


@composite
def violation_generator(draw,
                        callgraph1,
                        callgraph2,
                        option=option_generator(),
                        benchmark_name=strategies.text()):
    option = draw(option)
    fuzzing_jobs: List[FuzzingJob] = []
    target=BenchmarkRecord(draw(benchmark_name))
    for level in option.get_levels():
        fuzzing_jobs.append(FuzzingJob({option: level}, option, target=target))
    finished_fuzzing_jobs: List[FinishedFuzzingJob] = []
    cg1 = tempfile.NamedTemporaryFile(mode='w', delete=False)
    cg2 = tempfile.NamedTemporaryFile(mode='w', delete=False)
    result_directory = tempfile.TemporaryDirectory()
    with open(cg1.name, 'w') as f:
        f.writelines(callgraph1)
    with open(cg2.name, 'w') as f:
        f.writelines(callgraph2)
    for job, result in zip(fuzzing_jobs, [cg1, cg2]):
        finished_fuzzing_jobs.append(FinishedFuzzingJob(job, 0, result.name))

    reader = SimpleLineReader()
    checker = CallgraphViolationChecker(1, reader, output_folder=result_directory.name, write_to_files=False)
    violations: List[PotentialViolation] = checker.check_violations(finished_fuzzing_jobs)
    return violations


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