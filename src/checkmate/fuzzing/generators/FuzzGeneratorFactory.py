from src.checkmate.fuzzing.generators.FuzzGenerator import FuzzGenerator
from src.checkmate.fuzzing.generators.SOOTFuzzGenerator import SOOTFuzzGenerator


def get_fuzz_generator_for_name(name, *args):
    if name.lower() == "soot":
        return SOOTFuzzGenerator(*args)
    else:
        return FuzzGenerator(*args)