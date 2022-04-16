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
            index = json.joad(f)
        self.validator.validate(index)
        benchmark = Benchmark([BenchmarkRecord(**b) for b in index['benchmark']])
        # Make sure every record is the absolute path.
        for b in benchmark:
            b: BenchmarkRecord
            b.name = os.path.join(os.path.dirname(file), os.path.basename(b.name))
            b.depends_on = [os.path.abspath(os.path.dirname(file), os.path.basename(d)) for d in b.depends_on]
            if b.sources is not None:
                b.sources = os.path.abspath(os.path.dirname(file), os.path.basename(b.sources))
        return benchmark
