import copy
from typing import Dict

from src.checkmate.fuzzing.generators.FuzzGenerator import FuzzGenerator
from src.checkmate.models.Level import Level
from src.checkmate.models.Option import Option


class SOOTFuzzGenerator(FuzzGenerator):
    def process_config(self, config: str) -> Dict[Option, Level]:
        config_as_dict = dict()
        tokens = config.split(" ")
        where_to_remove = []
        for i in range(len(tokens)):
            if tokens[i] == '-p':
                # The phase option specification would be -p phase opt:setting,
                #  so we want to remove all three.
                where_to_remove.extend([i, i+1, i+2])
                # Skip the phase option because right now, that's specified in the option's tags.
                # However, this will cause us problems later on if two phases have options
                # that are named the same thing.
                phase_options = tokens[i+2].split(",")
                for phase_option in phase_options:
                    phase_option = phase_option.split(":")
                    option = self.model.get_option(phase_option[0])
                    config_as_dict[option] = option.get_level(phase_option[1])

        rest_of_config_string = ""
        for j in range(len(tokens)):
            if j not in where_to_remove:
                rest_of_config_string = rest_of_config_string + tokens[j] + " "
        rest_of_config_string = " ".join(tokens[:where_to_remove]) + " " + " ".join(tokens[where_to_remove+3:])
        rest_of_config: Dict[Option, Level] = super().process_config(rest_of_config_string)
        return {**config_as_dict, **rest_of_config}