This artifact works on Windows, Intel/Apple Silicon Macs, and Linux systems running Intel processors. Note that, if you are running on ARM architecture (e.g., Apple Silicon), Python will have to build Z3 from scratch, meaning your system must have CMake.

We have not tested on systems with AMD processors, but have no reason to believe there would be any issues.

In terms of software requirements, the user must have:
1. A Python executable of at least version 3.10, including the venv and development packages (`python3.XX-dev` and `python3.XX-venv` on Ubuntu). Note that Mac and Windows Python installers should already have these.
2. A C and C++ compiler, e.g., `gcc` and `g++`.
3. GNU `Make`
4. For ARM architectures, you may also require `CMake`.

For example, setting up these dependencies on Ubuntu 22.04 looks like:

```commandline
sudo apt install python3.11 python3.11-dev python3.11-venv g++ gcc make cmake
```

In addition, you must have a working Docker installation (https://docs.docker.com/get-docker/).

Running our full experiments takes tens of thousands of machine hours, so we have provided instructions on how to run 
a small subset of experiments and read/interpret the results. Please refer to INSTALL.md on setup instructions, and to README.md for usage examples.
