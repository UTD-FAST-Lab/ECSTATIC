#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


import importlib
import json
import logging
import os.path

from jsonschema.validators import RefResolver, Draft7Validator

from src.ecstatic.util.ApplicationCodeFilter import ApplicationCodeFilter
from src.ecstatic.util.JavaApplicationCodeFilter import JavaApplicationCodeFilter
from src.ecstatic.util.UtilClasses import Benchmark, BenchmarkRecord

logger = logging.getLogger(__name__)


def try_resolve_path(path: str, root: str = "/") -> str:
    path = os.path.basename(path)
    if path is None:
        return None
    logging.info(f'Trying to resolve {path} in {root}')
    if path.startswith("/"):
        path = path[1:]
    if os.path.exists(joined_path := os.path.join(root, path)):
        return os.path.abspath(joined_path)
    results = set()
    for rootdir, dirs, _ in os.walk(os.path.join(root, "benchmarks")):
        cur = os.path.join(os.path.join(root, "benchmarks"), rootdir)
        if os.path.exists(os.path.join(cur, path)):
            results.add(os.path.join(cur, path))
        for d in dirs:
            if os.path.exists(os.path.join(os.path.join(cur, d), path)):
                results.add(os.path.join(os.path.join(cur, d), path))
    match len(results):
        case 0: raise FileNotFoundError(f"Could not resolve path {path} from root {root}")
        case 1: return results.pop()
        case _: raise RuntimeError(f"Path {path} in root {root} is ambiguous. Found the following potential results: "
                                   f"{results}. Try adding more context information to the index.json file, "
                                   f"so that the path is unique.")


def validate(benchmark: BenchmarkRecord, root: str = "/") -> BenchmarkRecord:
    """
    Validates a benchmark, resolving each of its paths to an absolute path.
    Searches in the supplied root directory.
    Parameters
    ----------
    benchmark : The benchmark to validate.
    root : Where to look for the benchmark files

    Returns
    -------
    A resolved benchmark
    """
    logger.info(f'Original benchmark record is {benchmark}')
    benchmark.name = try_resolve_path(benchmark.name, root)
    benchmark.depends_on = [try_resolve_path(d, root) for d in benchmark.depends_on]
    benchmark.sources = [try_resolve_path(s, root) for s in benchmark.sources]
    benchmark.build_script = try_resolve_path(benchmark.build_script, root)
    logger.info(f'Resolved benchmark record to {benchmark}')
    return benchmark


class BenchmarkReader:
    def __init__(self,
                 schema: str = importlib.resources.path('src.resources.schema', 'benchmark.schema.json'),
                 application_code_filter: ApplicationCodeFilter = JavaApplicationCodeFilter()):
        self.schema = schema
        with open(schema, 'r') as f:
            self.schema = json.load(f)
        self.resolver = RefResolver.from_schema(self.schema)
        self.validator = Draft7Validator(self.schema, self.resolver)
        self.application_code_filter = application_code_filter

    def read_benchmark(self, file: str) -> Benchmark:
        with open(file, 'r') as f:
            index = json.load(f)
        self.validator.validate(index)
        benchmark = Benchmark([validate(BenchmarkRecord(**b)) for b in index['benchmark']])
        if self.application_code_filter is not None:
            benchmark = Benchmark([self.application_code_filter.find_application_packages(br) for br in benchmark.benchmarks])
        return benchmark


