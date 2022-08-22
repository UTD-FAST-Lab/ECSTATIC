import random
import tempfile
from typing import List

from hypothesis import strategies, assume
from hypothesis.strategies import composite

from src.ecstatic.models.Level import Level
from src.ecstatic.models.Option import Option
from src.ecstatic.models.Tool import Tool
from src.ecstatic.readers.SimpleLineReader import SimpleLineReader
from src.ecstatic.util.PartialOrder import PartialOrderType, PartialOrder
from src.ecstatic.util.PotentialViolation import PotentialViolation
from src.ecstatic.util.UtilClasses import FuzzingJob, BenchmarkRecord, FinishedFuzzingJob
from src.ecstatic.violation_checkers.CallgraphViolationChecker import CallgraphViolationChecker


@strategies.composite
def level(draw, option: Option, level_name=strategies.text()):
    return Level(option.name, draw(level_name))


@strategies.composite
def partial_order(draw,
                  option,
                  type=strategies.one_of(strategies.just(PartialOrderType.MORE_SOUND_THAN),
                                         strategies.just(PartialOrderType.MORE_PRECISE_THAN))):
    left = draw(level(option))
    right = draw(level(option))
    po_type = draw(type)
    return PartialOrder(left, right, po_type, option)


@strategies.composite
def categorical_option(draw,
                       name=strategies.text(),
                       min_levels=0,
                       max_levels=100,
                       min_level_settings=0,
                       max_level_settings=100,
                       partial_order_strategy=strategies.one_of(strategies.just(None),
                                       strategies.just(PartialOrderType.MORE_SOUND_THAN),
                                       strategies.just(PartialOrderType.MORE_PRECISE_THAN))):
    levels = draw(strategies.lists(
        strategies.lists(strategies.text(), min_size=min_level_settings, max_size=max_level_settings),
        min_size=min_levels,
        max_size=max_levels))
    option = Option(name)
    for level_list in levels:
        state = draw(partial_order_strategy)
        for level in level_list:
            option.add_level(level)
        for ix in range(len(level_list) - 1):
            match state:
                case PartialOrderType.MORE_SOUND_THAN:
                    option.set_more_sound_than(level_list[ix], level_list[ix + 1])
                case PartialOrderType.MORE_PRECISE_THAN:
                    option.set_more_precise_than(level_list[ix], level_list[ix + 1])
                case None:
                    pass
    return option


@strategies.composite
def option(draw):
    """
    Add more potential draws here if I implement other strategies.
    """
    return draw(categorical_option)


@strategies.composite
def tool(draw, name=strategies.text(),
         options=strategies.lists(option)):
    tool: Tool = Tool(draw(name))
    for o in draw(options):
        tool.add_option(o)

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
    target = BenchmarkRecord(draw(benchmark_name))
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
