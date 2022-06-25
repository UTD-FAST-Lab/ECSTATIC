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
import logging
import os
import subprocess
from importlib.resources import path
from pathlib import Path

import docker
from docker.models.containers import Container

client = docker.from_env()
logger = logging.getLogger(__name__)


def build_image(tool: str, nocache: bool = False):
    env = os.environ
    env['DOCKER_BUILDKIT'] = '1'
    if tool == 'base':
        logger.info("Creating base image")
        cmd = ['docker', 'build', '.', '-f', 'base_image.dockerfile', '-t', get_image_name(tool)]
        print(f'Building docker image with command {" ".join(cmd)}')
        # image = client.images.build(path=".", dockerfile="base_image.dockerfile", tag=get_image_name(tool), nocache=nocache)
        # with open('base_image.dockerfile', 'rb') as df:
        #     logging.info("Building base image.")
        #     image = client.build(fileobj=df, tag=get_image_name(tool))
    else:
        logger.info(f"Building image for {tool}")
        cmd = ['docker', 'build', str(importlib.resources.path(f"src.resources.tools", tool)),
               '-t', get_image_name(tool)]
        print(f'Building docker image with command {" ".join(cmd)}')
    if nocache:
        cmd.append('--no-cache')
    subprocess.run(cmd)


def start_runner(tool: str, benchmark: str, task: str, args):
    # PYTHONENV=/ecstatic
    # run build benchmark script
    command = f'tester {tool} {benchmark} -t {task} -j {args.jobs} --fuzzing-timeout {args.fuzzing_timeout}'
    if args.timeout is not None:
        command += f' --timeout {args.timeout}'
    if args.verbose > 0:
        command += f' -{"".join(["v" for _ in range(args.verbose)])}'
    if args.no_delta_debug:
        command += f' --no-delta-debug'

    print(f'Starting container with command {command}')
    Path(args.results_location).mkdir(parents=True, exist_ok=True)
    cntr: Container = client.containers.run(
        image=get_image_name(tool),
        command="/bin/bash",
        detach=True,
        tty=True,
        volumes={os.path.abspath(args.results_location): {"bind": "/results", "mode": "rw"}},
        auto_remove=True)
    _, log_stream = cntr.exec_run(cmd=command, stream=True)
    for l in log_stream:
        print(l.decode())
    print('Run finished!')
    # print('Removing container....')
    # cntr.stop()
    # cntr.remove()
    # print('Container removed!')
    print(f"Results are in {args.results_location}")


def get_image_name(tool: str):
    if tool == 'base':
        return 'ecstatic/base-image'
    return f'ecstatic/tools/{tool}'
