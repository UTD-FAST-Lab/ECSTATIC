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

from importlib.resources import files, as_file
import logging
import os
import subprocess
from pathlib import Path

import docker
from docker.models.containers import Container

client = docker.from_env()
logger = logging.getLogger(__name__)


def build_image(tool: str, nocache: bool = False):
    env = os.environ
    os.environ["DOCKER_DEFAULT_PLATFORM"] = "linux/amd64"
    if tool == 'base':
        logger.info("Creating base image")
        cmd = ['docker', 'build', '.', '-f', 'base_image.dockerfile', '-t', get_image_name(tool)]
        print(f'Building docker image with command {" ".join(cmd)}')
    else:
        logger.info(f"Building image for {tool}")

        # Determine platform
        import platform
        machine_string = platform.machine()
        if "arm" in machine_string:
            machine_string = "arm64"
        elif "x86_64" in machine_string or "amd" in machine_string:
            machine_string = "amd64"

        with as_file(files("src.resources.tools").joinpath(tool)) as tool:
            cmd = ['docker', 'build', str(tool),'-t', get_image_name(tool), "--build-arg", f"platform={machine_string}"]
        print(f'Building docker image with command {" ".join(cmd)}')
    if nocache:
        cmd.append('--no-cache')
    subprocess.run(cmd)


def start_runner(tool: str, benchmark: str, task: str, args):
    # PYTHONENV=/ecstatic
    # run build benchmark script
    command = f'tester {tool} {benchmark} -t {task} -j {args.jobs} --fuzzing-timeout {args.fuzzing_timeout} ' \
              f'--delta-debugging-mode {args.delta_debugging_mode} --seed {args.seed} ' \
              f'--fuzzing-strategy {args.fuzzing_strategy.name.lower()}'
    if args.timeout is not None:
        command += f' --timeout {args.timeout}'
    if args.verbose > 0:
        command += f' -{"".join(["v" for _ in range(args.verbose)])}'
    if args.full_campaigns:
        command += f' --full-campaigns'
    if args.hdd_only:
        command += f' --hdd-only'

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
        try:
            print(l.decode())
        except Exception as e:
            logger.exception("Couldn't decode line from output.")
    print('Run finished!')
    # print('Removing container....')
    # cntr.stop()
    # cntr.remove()
    # print('Container removed!')
    print(f"Results are in {args.results_location}")


def get_image_name(tool: str):
    if isinstance(tool, Path):
        tool = tool.name
    if tool == 'base':
        return 'ecstatic/base-image'
    return f'ecstatic/tools/{tool}'
