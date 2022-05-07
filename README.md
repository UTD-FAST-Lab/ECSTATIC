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
We know ECSTATIC can successfully build on Ubuntu hosts, and cannot successfully 
build on M1 Macs as of April 2022.

# Usage

We recommend creating a virtual environment for ECSTATIC. In order to install 
CheckMate's dependencies, from the root directory of the repository, run

`python -m pip install -r requirements.txt`

Where `python` points to a Python executable of at least version 3.10.0. 
This will install all of the Python dependencies required. Then, in order to install
the application, run

`python -m pip install .`

If you wish to work on ECSTATIC's code, run `python -m pip install -e .`; the `-e` 
flag builds in-place, so changes are immediately reflected in the executable.

This installation will put two executables on your system PATH: `checkmate` and
`tester`. `ECSTATIC` is the command you run from your host, while `tester` 
is the command you run from inside the Docker container (under normal usage, a user
will never invoke `tester` themselves, but it can be useful for debugging to skip
container creation.)

Simply run `ECSTATIC --help` from anywhere in order to see the helpdoc on how to
invoke ECSTATIC.
