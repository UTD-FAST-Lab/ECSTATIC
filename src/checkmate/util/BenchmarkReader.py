#  CheckMate: A Configuration Tester for Static Analysis
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
import os.path

from jsonschema.validators import RefResolver, Draft7Validator

from src.checkmate.util.UtilClasses import Benchmark, BenchmarkRecord


class BenchmarkReader:
    def __init__(self,
                 schema: str = importlib.resources.path('src.resources.schema', 'benchmark.schema.json')):
        self.schema = schema
        with open(schema, 'r') as f:
            self.schema = json.load(f)
        self.resolver = RefResolver.from_schema(self.schema)
        self.validator = Draft7Validator(self.schema, self.resolver)

    def read_benchmark(self, file: str) -> Benchmark:
        with open(file, 'r') as f:
            index = json.load(f)
        self.validator.validate(index)
        benchmark = Benchmark([BenchmarkRecord(**b) for b in index['benchmark']])
        # Make sure every record is the absolute path.
        for b in benchmark.benchmarks:
            b: BenchmarkRecord
            b.name = os.path.join(os.path.dirname(file), os.path.basename(b.name))
            b.depends_on = [os.path.abspath(os.path.join(os.path.dirname(file), os.path.basename(d))) for d in b.depends_on]
            if b.sources is not None:
                b.sources = os.path.abspath(os.path.join(os.path.dirname(file), os.path.basename(b.sources)))
        return benchmark
