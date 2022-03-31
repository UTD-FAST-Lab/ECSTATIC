import logging
import os
from typing import List

import docker
from importlib.resources import path

client = docker.APIClient(base_url='unix://var/run/docker.sock')


def build_image(tool: str):
    if tool == 'base':
        logging.info("Creating base image")
        image = client.build(dockerfile="./base_image.dockerfile", tag=get_image_name(tool))
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


def start_runner(tool: str, benchmarks: List[str], tasks: List[str]):
    # PYTHONENV=/checkmate
    # run build benchmark script
    command = f'tester {tool} {" ".join(benchmarks)} -t {" ".join(tasks)}'
    client.create_container(image=get_image_name(tool), command=command)


def get_image_name(tool: str):
    if tool == 'base':
        return 'checkmate/base-image'
    return f'checkmate/tools/{tool}'
