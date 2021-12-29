import json
import logging
import os.path


def __get_configuration():
    try:
        with open('./resources/config.json', 'r') as f:
            raw_content = json.load(f)
            for k, _ in raw_content.items():
                if k != "variables":
                    for k1, v1 in raw_content['variables'].items():
                        raw_content[k] = raw_content[k].replace(k1, raw_content[v1])
    except FileNotFoundError as fe:
        logging.critical("Config file not found. Looking in "
                         "./resources/config.json. Try running again from "
                         "the checkmate root directory?")
    for _, v in raw_content.items():
        if not os.path.exists(v):
            raise FileNotFoundError(f'Could not find file {v} from config.json')

    return raw_content


configuration = __get_configuration()