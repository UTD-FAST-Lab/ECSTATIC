import json
import logging

def __get_configuration():
    try:
        with open('./resources/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError as fe:
        logging.critical("Config file not found. Looking in "
                         "./resources/config.json. Try running again from "
                         "the checkmate root directory?")

configuration = __get_configuration()