from .flowdroid_grammar import FlowdroidGrammar
from fuzzingbook.GrammarCoverageFuzzer import GrammarCoverageFuzzer
from fuzzingbook.Grammars import convert_ebnf_grammar
from ..models import Option, Tool
import pickle
import random
import copy
from typing import Dict, List


def main(model_location: str, number_configs: int):
    flowdroid_ebnf_grammar = FlowdroidGrammar.getGrammar()
    flowdroid_grammar = convert_ebnf_grammar(flowdroid_ebnf_grammar)
    fuzzer = GrammarCoverageFuzzer(flowdroid_grammar)
    with open(model_location, 'rb') as f:
        model = pickle.load(f)
    for i in range(number_configs):
        config = process_config(fuzzer.fuzz())
        candidates = mutate_config(model, config)
        choice = random.choice(candidates)
        print(f'Pair of configs is {config}, {choice}. Different on {[k for k in choice.keys() if k not in config.keys() or config[k] != choice[k]]}.')
    

def process_config(config: str) -> Dict[str, str]:
    i = 0
    tokens: List[str] = config.split(' ')
    result: Dict[str, str] = {}
    while(i < len(tokens)):
        if tokens[i].startswith('--'):
            if i == (len(tokens) - 1) or tokens[i+1].startswith('--'):
                result[tokens[i].replace('--', '')] = "TRUE"
                i = i + 1
            else:
                result[tokens[i].replace('--', '')] = tokens[i+1]
                i = i + 2
        else:
            i = i + 1 # skip
    return result


def mutate_config(model: Tool, config: Dict[str, str]):
    """
    For each option, consult the model for settings that are different.
    Add it to the configuration and randomly select one/some as a mutant.
    """
    candidates = list()
    options: List[Option] = model.get_options()

    for o in options:
#        import pdb; pdb.set_trace()
        for level in o.get_levels():
            if o.name not in config:
                config[o.name] = o.get_default()
            current_setting = config[o.name]
            if level == config[o.name]:
                 continue
            if (o.soundness_compare(level, config[o.name]) != 0):
                config_copy = copy.deepcopy(config)
                config_copy[o.name] = level
                candidates.append(config_copy)
    return candidates
                

    
if __name__ == '__main__':
    main()
