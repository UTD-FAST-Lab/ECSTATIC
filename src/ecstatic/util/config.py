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


import importlib.resources
import json
import logging
import os.path

# TODO: We should use setup.cfg for these things.
def __get_configuration():
    with open(importlib.resources.path('src.resources', 'config.json'), 'r') as f:
        raw_content = json.load(f)
        for k, _ in raw_content.items():
            if k != "variables":
                for k1, v1 in raw_content['variables'].items():
                    raw_content[k] = raw_content[k].replace(k1, raw_content[v1])
        raw_content.pop('variables')
    # for _, v in raw_content.items():
    #     if not os.path.exists(v):
    #         raise FileNotFoundError(f'Could not find file {v} from config.json')
    return raw_content


configuration = __get_configuration()