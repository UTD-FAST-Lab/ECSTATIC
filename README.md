# ECSTATIC

ECSTATIC (Extensible, Customizable Static Analysis Tester Informed by Configuration) is a flexible tool that can be used to test configurable 
static analyses on a variety of benchmarks.
ECSTATIC can be extended to use alternative analyses, but currently, it can run 
call graph analyses on WALA, SOOT, and DOOP, as well as taint analysis on Android
applications using FlowDroid.

# Prerequisites
This application is written for Python version >= 3.10.0. Furthermore, 
ECSTATIC runs its analyses in Docker containers in order to maintain consistent
environments across runs, so you must have a working Docker installation.
We know ECSTATIC can successfully build on Ubuntu and Windows hosts, and cannot successfully 
build on M1 Macs as of April 2022 (specifically, the build process hangs when trying to build Z3 for Python.
If you know how to fix this, feel free to make a pull request!)

# Usage

We recommend creating a virtual environment for ECSTATIC. To do so, run

`python -m venv <name_of_virtual_environment>`

where 'python' points to a python 3.8 or higher installation. This will create a new folder. If, for example, you named your folder 'venv', then
you can activate it as follows:

`source ./venv/bin/activate`

In order to install ECSTATIC's dependencies, from the root directory of the repository, run

`python -m pip install -r requirements.txt`

Where `python` points to a Python executable of at least version 3.8.0. 
This will install all of the Python dependencies required. Then, in order to install
the application, run

`python -m pip install -e .`

We require the `-e` to build in-place. Currently, omitting this option will cause the Dockerfile resolution to fail when we try to build tool-specific images.

This installation will put three executables on your system PATH: `dispatcher`, `tester`, and `deltadebugger`.
`dispatcher` is the command you run from your host, while `tester` is the command you run from inside the Docker container (under normal usage, a user
will never invoke `tester` themselves, but it can be useful for debugging to skip
container creation.)

Simply run `dispatcher --help` from anywhere in order to see the helpdoc on how to
invoke ECSTATIC.

# Extending with New Tools

To add a new tool to ECSTATIC, you must take the following steps:
1. Create a new Dockerfile for your tool under `src/resources/tools/<tool_name>`.
The Dockerfile must create an image that inherits from ECSTATIC's base image, and builds the tool. See some of the 
existing Dockerfiles we have for examples.
2. Add a new class that inherits from [AbstractCommandLineToolRunner.py](src/ecstatic/runners/AbstractCommandLineToolRunners.py) 
in order to run the tool. Specifically, you must override the `try_run_job` method. If your tool is able to be run relatively simply
(i.e., only by setting command line options), then you might find it easier to 
extend [CommandLineToolRunner.py](src/ecstatic/runners/CommandLineToolRunner.py). See [SOOTRunner.py](src/ecstatic/runners/SOOTRunner.py) 
and [WALARunner.py](src/ecstatic/runners/WALARunner.py) for examples of classes that extend CommandLineToolRunner, and 
[DOOPRunner.py](src/ecstatic/runners/DOOPRunner.py) and [FlowDroidRunner.py](src/ecstatic/runners/FlowDroidRunner.py) for examples of more complex
runners that inherit from AbstractCommandLineToolRunner.py.
3. Add logic to [RunnerFactory.py](src/ecstatic/runners/RunnerFactory.py) to initialize your new runner given the 
name of the tool.
4. Add a new class that inherits from [AbstractRunner.py](src/ecstatic/readers/AbstractReader.py) to read the results of your tool.
The `import_file` method of this class accepts a file name, and returns an iterable of results.
In order to detect violations, it is important that equality be defined correctly between the results.
5. Add logic to [ReaderFactory.py](src/ecstatic/readers/ReaderFactory.py) that will return the appropriate reader given the task and tool name.
6. Depending on how you want to detect violations, you may need to add a new violation checker that inherits from 
[AbstractViolationChecker.py](src/ecstatic/violation_checkers/AbstractViolationChecker.py). The default behavior is 
to just check equality between records. However, if you need to determine ground truths, or you need to filter results 
(as we do in callgraph analyses), then you might need your own class. If you implement a new class, be sure to add logic to
[ViolationCheckerFactory.py](src/ecstatic/violation_checkers/ViolationCheckerFactory.py).
7. That's it!

# Extending with New Benchmarks
Adding a new benchmark is relatively simple.
1. Add a new folder to [src/resources/benchmarks](src/resources/benchmarks), with the name of your benchmark.
2. In that folder, create a `build.sh` script that will pull the benchmark code, build it, and put it under 
`/benchmarks/<benchmark_name>` in the Docker container. Add an `index.json` file specifying the programs you want to 
run. The resolver for this file will automatically resolve paths so long as they are unique in the `/benchmarks`
directory.  
