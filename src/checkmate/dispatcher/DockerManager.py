import importlib
import io
import logging
import os
import subprocess
import tarfile
import time
from typing import List

import docker
from importlib.resources import path

client = docker.APIClient(base_url='unix://var/run/docker.sock')


def build_image(tool: str, nocache=False):
    if tool == 'base':
        logging.info("Creating base image")
        image = client.build(path=".", dockerfile="base_image.dockerfile", tag=get_image_name(tool), nocache=nocache, rm=nocache, forcerm=nocache)
        # with open('base_image.dockerfile', 'rb') as df:
        #     logging.info("Building base image.")
        #     image = client.build(fileobj=df, tag=get_image_name(tool))
    else:
        with path('src.resources', 'tools') as tools_dir:
            with open(os.path.join(tools_dir, tool, 'Dockerfile'), 'rb') as df:
                logging.info(f"Building image for {tool}")
                image = client.build(fileobj=df, tag=get_image_name(tool))

    response = [line for line in image]
    print(response)


def start_runner(tool: str, benchmark: str, task: str):
    # PYTHONENV=/checkmate
    # run build benchmark script
    command = f'tester {tool} {benchmark} -t {task}'
    logging.info(f'Starting container with command {command}')
    cntr = client.containers.run(image=get_image_name(tool), command=command, detach=False)
    logging.info(f"Cntr is {cntr}")
    id = cntr['Id']
    cmd =['docker', 'cp', f'{id}:/results', os.path.join(importlib.resources.path("results", ""),
                           f"{tool}_{benchmark}_{task}_{time.time()}")]
    logging.info(f'Docker cp command is {" ".join(cmd)}')
    subprocess.run(cmd)



def get_image_name(tool: str):
    if tool == 'base':
        return 'checkmate/base-image'
    return f'checkmate/tools/{tool}'
