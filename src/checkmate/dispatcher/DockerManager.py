import os
import docker
from importlib.resources import path

client = docker.APIClient(base_url='unix://var/run/docker.sock')

def build_image(tool: str):
    if tool == 'base':
        with open('base_image.dockerfile', 'rb') as df:
            image = client.build(fileobj=df, tag=get_image_name(tool))
    else:
        with path('src.resources', 'tools') as tools_dir:
            with open(os.path.join(tools_dir, tool, 'Dockerfile'), 'rb') as df:
                image = client.build(fileobj=df, tag=get_image_name(tool))


    response = [line for line in image]
    print(response)

def start_runner(tool: str, benchmarks: list, tasks: list):
    # PYTHONENV=/checkmate
    # run build benchmark script
    command = f'python3 /checkmate/src/checkmate/fuzzing/tooltester.py {tool} {' '.join(benchmarks)} -t {' '.join(tasks)}'
    client.create_container(image=get_image_name(tool), command=command)

def get_image_name(tool: str):
    if tool == 'base':
        return 'checkmate/base-image'
    return f'checkmate/tools/{tool}'
