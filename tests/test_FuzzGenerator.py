import importlib

from src.checkmate.fuzzing import tooltester
from src.checkmate.fuzzing.generators.FuzzGenerator import FuzzGenerator
from src.checkmate.util.UtilClasses import Benchmark, BenchmarkRecord

b: Benchmark = Benchmark([BenchmarkRecord(os.path.abspath(importlib.resources.path("src.resources.benchmarks.test", "CallSiteSensitivity1.jar")))])


def test_FuzzGenerator_first_run():
    fg = FuzzGenerator(importlib.resources.path("src.resources.configuration_spaces", "soot_config.json"),
                       importlib.resources.path("src.resources.grammars", "soot_grammar.json"),
                       tooltester.build_benchmark("test"))


