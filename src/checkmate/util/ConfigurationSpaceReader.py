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

import importlib.resources
import json
import logging
import os

from jsonschema.validators import RefResolver, Draft7Validator
from src.checkmate.models.Tool import Tool


class ConfigurationSpaceReader:
    def __init__(self,
                 schema_directory: str = importlib.resources.path('src.resources', 'schema'),
                 master_schema: str = importlib.resources.path('src.resources.schema', 'configuration_space.schema.json')):
        self.validator: Draft7Validator = None
        self.resolver: RefResolver = None
        self.__setup(schema_directory, master_schema)

    def __setup(self, schema_directory: str, master_schema: str):
        # Open all schemata
        schemata = {}
        for root, _, files in os.walk(schema_directory):
            for f in files:
                if f.endswith('.json'):
                    with open(os.path.join(root, f)) as fi:
                        schemata[f] = json.load(fi)

        schemata_store = {v["$id"]: v for k, v in schemata.items()}
        self.resolver = RefResolver.from_schema(schemata[os.path.basename(master_schema)], store=schemata_store)
        self.validator = Draft7Validator(schemata[os.path.basename(master_schema)], self.resolver)

    def read_configuration_space(self, file: str) -> Tool:
        with open(file) as f:
            config_space = json.load(f)

        self.validator.validate(config_space)
        logging.info(f"Config space is {config_space}")
        tool = Tool.from_dict(config_space)
        logging.info(tool.get_options())
        return tool
