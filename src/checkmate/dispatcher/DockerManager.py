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

def build_image(tool: str, nocache=False):
    env = os.environ
    env['DOCKER_BUILDKIT'] = '1'
    if tool == 'base':
        logger.info("Creating base image")
        subprocess.run(['docker', 'build', '.', '-f', 'base_image.dockerfile', '-t', get_image_name(tool)])
        # image = client.images.build(path=".", dockerfile="base_image.dockerfile", tag=get_image_name(tool), nocache=nocache)
        # with open('base_image.dockerfile', 'rb') as df:
        #     logging.info("Building base image.")
        #     image = client.build(fileobj=df, tag=get_image_name(tool))
    else:
        logger.info(f"Building image for {tool}")
        cmd = ['docker', 'build', os.path.abspath(importlib.resources.path(f"src.resources.tools", tool)),
                        '-t', get_image_name(tool)]
        logger.info(cmd)
        subprocess.run(cmd)


def start_runner(tool: str, benchmark: str, task: str, jobs: int, campaigns: int):
    # PYTHONENV=/checkmate
    # run build benchmark script
    command = f'tester {tool} {benchmark} -t {task} -j {jobs} -c {campaigns}'
    print(f'Starting container with command {command}')
    results_folder = os.path.abspath(importlib.resources.path("results", ""))
    Path(results_folder).mkdir(parents=True, exist_ok=True)
    cntr: Container = client.containers.run(
        image=get_image_name(tool),
        command="/bin/bash",
        detach=True,
        tty=True,
        volumes={os.path.abspath(results_folder) : {"bind": "/results", "mode": "rw"}},
        auto_remove=True)
    _, log_stream = cntr.exec_run(cmd=command, stream=True)
    for l in log_stream:
        print(l.decode())
    print('Run finished!')
    # print('Removing container....')
    # cntr.stop()
    # cntr.remove()
    # print('Container removed!')
    print(f"Results are in {results_folder}")


def get_image_name(tool: str):
    if tool == 'base':
        return 'checkmate/base-image'
    return f'checkmate/tools/{tool}'
