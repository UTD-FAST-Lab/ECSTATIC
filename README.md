# ECSTATIC

## What This Artifact Does
ECSTATIC (Extensible, Customizable Static Analysis Tester Informed by Configuration) is a flexible tool that can be used to test configurable 
static analyses on a variety of benchmarks.
ECSTATIC can be extended to use alternative analyses and benchmarks, but currently, it can run 
call graph analyses on WALA, SOOT, and DOOP, as well as taint analysis on Android
applications using FlowDroid.

## How To Replicate the Experiments From the Paper

Please follow the instructions in INSTALL.md before trying the instructions in this section.

***For artifact reviewers:*** These experiments took thousands of hours of machine time to perform. We provide smaller experiments to verify the functionality of the artifact in the next section.
### Base Testing Phase Only
The following eight commands will run the base testing phase for all tool/benchmark combinations, without delta debugging or random testing. The results from these experiments correspond to the left half of each numerical cell in Table 1.
```commandline
dispatcher -t soot -b cats-microbenchmark --tasks cg --timeout 15
dispatcher -t soot -b dacapo-2006 --tasks cg --timeout 30
dispatcher -t doop -b cats-microbenchmark --tasks cg --timeout 30
dispatcher -t doop -b dacapo-2006 --tasks cg --timeout 45
dispatcher -t wala -b cats-microbenchmark --tasks cg --timeout 15
dispatcher -t wala -b dacapo-2006 --tasks cg --timeout 30
dispatcher -t flowdroid -b droidbench --tasks taint --timeout 15
dispatcher -t flowdroid -b fossdroid --tasks taint --timeout 30
```

### Random Testing

Random testing is controlled through the following command line parameters:

-`--fuzzing-timeout`: Timeout in minutes. For our experiments, this should be (24*60)=1440. By default, this is 0, which tells ECSTATIC to stop after baseline testing.

-`--full-campaigns`: Passing this option performs exhaustive testing. Otherwise, non-exhaustive testing is performed.

-`--seed`: The random seed that is used for random testing. For our experiments, we used the seeds 18331 and 3213.

To perform the random testing experiments, run the following commands.

```commandline
# Exhaustive Testing
dispatcher -t soot -b cats-microbenchmark --tasks cg --timeout 15 --fuzzing-timeout 1440 --full-campaigns
dispatcher -t soot -b dacapo-2006 --tasks cg --timeout 30 --fuzzing-timeout 1440 --full-campaigns
dispatcher -t wala -b cats-microbenchmark --tasks cg --timeout 15 --fuzzing-timeout 1440 --full-campaigns
dispatcher -t wala -b dacapo-2006 --tasks cg --timeout 30 --fuzzing-timeout 1440 --full-campaigns
dispatcher -t flowdroid -b droidbench --tasks taint --timeout 15 --fuzzing-timeout 1440 --full-campaigns
dispatcher -t flowdroid -b fossdroid --tasks taint --timeout 30 --fuzzing-timeout 1440 --full-campaigns

# Non-Exhaustive Testing
dispatcher -t soot -b cats-microbenchmark --tasks cg --timeout 15 --fuzzing-timeout 1440
dispatcher -t soot -b dacapo-2006 --tasks cg --timeout 30 --fuzzing-timeout 1440
dispatcher -t wala -b cats-microbenchmark --tasks cg --timeout 15 --fuzzing-timeout 1440
dispatcher -t wala -b dacapo-2006 --tasks cg --timeout 30 --fuzzing-timeout 1440
dispatcher -t flowdroid -b droidbench --tasks taint --timeout 15 --fuzzing-timeout 1440
dispatcher -t flowdroid -b fossdroid --tasks taint --timeout 30 --fuzzing-timeout 1440
```

*Note that we ran our experiments with 4 cores each. Running with a different number of cores may result in a drastically different number of testing iterations, in addition to differences caused by hardware differences, system workload, etc.*

### Delta Debugging

Delta debugging is controlled through two command-line parameters:

-`-d {none,violation}` Controls whether to perform delta debugging. Setting `-d` to `none` (default) performs no delta debugging. Setting `-d` to `violation` performs violation-aware delta debugging after testing.

-`--hdd-only` Passing this will only do hierarchical delta debugging, as opposed to the two-phase delta debugging described in Section III.C.
'

To replicate our delta debugging experiments (RQ2), run the following commands:

```commandline
# Base Testing With Two-Phase Delta Debugging
dispatcher -t soot -b cats-microbenchmark --tasks cg --timeout 15 -d violation
dispatcher -t soot -b dacapo-2006 --tasks cg --timeout 30 -d violation
dispatcher -t wala -b cats-microbenchmark --tasks cg --timeout 15 -d violation
dispatcher -t wala -b dacapo-2006 --tasks cg --timeout 30 -d violation
dispatcher -t flowdroid -b droidbench --tasks taint --timeout 15 -d violation
dispatcher -t flowdroid -b fossdroid --tasks taint --timeout 30 -d violation

# Base Testing With HDD-Only Delta Debugging
dispatcher -t soot -b cats-microbenchmark --tasks cg --timeout 15 -d violation --hdd-only
dispatcher -t soot -b dacapo-2006 --tasks cg --timeout 30 -d violation --hdd-only
dispatcher -t wala -b cats-microbenchmark --tasks cg --timeout 15 -d violation --hdd-only
dispatcher -t wala -b dacapo-2006 --tasks cg --timeout 30 -d violation --hdd-only
dispatcher -t flowdroid -b droidbench --tasks taint --timeout 15 -d violation --hdd-only
dispatcher -t flowdroid -b fossdroid --tasks taint --timeout 30 -d violation --hdd-only
```

## Smaller Experiments for Artifact Reviewers

Please follow the instructions in INSTALL.md before trying the experiments in this section.

We suggest artifact reviewers use FlowDroid, SOOT, or WALA, as these tools are much faster relative to DOOP, which 
is slow to build and takes a lot of system memory.

We have provided small versions of the CATS Microbenchmark, Droidbench, and DaCapo-2006 under the names `cats-small`. 
`droidbench-small`, and `dacapo-small`, respectively. These benchmarks each contain one program which exhibited a violation:

- `cats-small` contains *Ser1.jar*, which exhibits a violation on WALA, and *Unsafe1.jar*, which exhibits a violation on SOOT.
- `droidbench-small` contains *ActivityLifecycle1.apk*, on which we detected the bug in FlowDroid's *codeelimination* option as described in Figure 1.
- `dacapo-small` contains *hsqldb.jar*, which exhibits a violation on WALA and can be reduced by 99% in the delta debugging phase.

For example, to run FlowDroid on `droidbench-small`, run the following command:

```commandline
dispatcher -t flowdroid -b droidbench-small --tasks taint
```

## How to Read ECSTATIC's Output

By default, ECSTATIC creates a *results* folder for its results, but the location of the results can be controlled with the `--results-location` option.

We explain the results of ECSTATIC through the example above, where we run FlowDroid on the `droidbench-small` benchmark.

```commandline
results
|- flowdroid
|  |- droidbench-small
|  |  |- campaign0
|  |  |  |- 3c2c6c9d6e896c028463ca607b7fce7a_ActivityLifecycle1.apk.raw
|  |  |  |- 4f9b34cf1904a0ff769463243bdcfe18_ActivityLifecycle1.apk.raw
|  |  |  |- configurations
|  |  |  |  |- 3c2c6c9d6e896c028463ca607b7fce7a
|  |  |  |  |- 4f9b34cf1904a0ff769463243bdcfe18
|  |  |  |  |- ...
|  |  |  |- shell_files
|  |  |  |- xml_scripts
|  |  |  |- violations
|  |  |  |  |- VIOLATION
|  |  |  |  |  |- TRANSITIVE
|  |  |  |  |  |- DIRECT
|  |  |  |  |  |  |- <violation_folder>
|  |  |  |  |  |  |  |- ActivityLifecycle1.apk.json
|  |  |  |  |  |  |  |- ...
|  |  |  |- delta_debugging
|  |  |  |  |- violations
|  |  |  |  |  |- <configuration>
|  |  |  |  |  |  |- <violation_folder>/<benchmark>/0
|  |  |  |  |  |  |  |- log.txt
|  |  |  |  |  |  |  |- benchmarks
|  |  |  |  |  |  |  |- <temporary folders>
|  |  |- <seed>
|  |  |  |- ...
```

We begin in the `campaign0` folder. We refer to each iteration of testing as a "campaign" -- "campaign0" corresponds to the base configuration testing phase. If random testing is performed, an additional folder with the random seed used will be added (represented as `<seed>` below).

Configurations in the results are represented as hash value. You can see what configuration a hash value represents by looking in the configuration folder. In this example, configuration 4f9b34cf1904a0ff769463243bdcfe18 corresponds to the configuration `--codeelimination REMOVECODE`

At the top level of the folder are raw results, which have the `.raw` extension. These are the results produced by the tool (in this case, taint flows in AQL-Answer format). These results are consumed by the *ToolReader* implementation.

The results of violation detection and delta debugging are in the `violation` and `delta_debugging` folders, respectively. The `violation` folder maintains all comparison results, with violations being in the `VIOLATION` folder. The `VIOLATION` folder has two subfolders: `DIRECT` (for direct violations) and `TRANSITIVE` (for transitive violations). Within these folders we first encounter the "violation folder", which has the following structure:

`<hash1>/<hash2>/<partial_order(s)>`

In our example, one such directory is: `4f9b34cf1904a0ff769463243bdcfe18/3c2c6c9d6e896c028463ca607b7fce7a/codeelimination/REMOVECODE/MST/DEFAULT`, which should be read as containing all the violations obtained by comparing configurations `4f9b...` and `3c26...` on the partial order *codeelimination.REMOVECODE* is at least as sound as *codeelimination.DEFAULT* (precision partial orders will use `MPT` rather than `MST`).

Within these directories are JSON files that contain violation records. Each input program with which a violation is detected will produce a JSON file. The JSON file lists the two configurations that were compared and the differences that resulted in the violation being detected.

Delta debugging results use a similar directory structure as violations, with the input program as an additional folder. If delta debugging was successful, this folder will contain a `log.txt` containing the statistics for the delta debugging run. `benchmarks` will contain a full copy of the input programs, so navigate to the location of the input being delta debugged to view the reduced source code.  

## Producing Results

We provide two Jupyter notebooks, [scripts/analysis/rq1.ipynb](scripts/analysis/rq1.ipynb) and [scripts/analysis/rq2.ipynb](scripts/analysis/rq2.ipynb) to produce the figures for RQ1 and RQ2 respectively. These scripts expect CSvs as input, which are generated by [scripts/generate_csvs.py](scripts/generate_csvs.py) and [scripts/generate_delta_debugging_reports.py](scripts/generate_delta_debugging_reports.py), respectively.

Both of these scripts work the same way, in that they proces a list of results from stdin and produce CSVs. So, for example, to use RQ1, first construct a `find` command (or any other shell utility you prefer) to collect all of the violation JSON files you are interested in and pipe it to the script. For example, from your results folder, run:

```commandline
# RQ1
find . -type f -wholename '*/VIOLATION/DIRECT/*.json' | python scripts/generate_csvs.py > /violation/report/location.csv

# RQ2
find . -type f -name 'log.txt' | python scripts/generate_delta_debugging_reports.py > /delta/debugging/report/location.csv
```

*Important: The scripts assume that your results folder is called "results". If you changed the name of this folder, change the appropriate places in the python scripts (marked by comments).*

The Jupyter notebooks have comments matching figures to the locations in the paper.

## Extending with New Tools

To add a new tool to ECSTATIC, you must take the following steps:
1. Create a new Dockerfile for your tool under `src/resources/tools/<tool_name>`.
The Dockerfile must create an image that inherits from ECSTATIC's base image, and builds the tool. See some of the 
existing Dockerfiles we have for examples.
2. Specify the configuration space and grammar in `src/resources/configuration_spaces/<tool_name>_config.json` and `src/resources/grammars/{tool_name>_grammar.json` respectively. Grammars are specified in the same format as Zeller's "The Fuzzing Book" https://www.fuzzingbook.org/html/Grammars.html, and configuration spaces are specified according to the schema `src/resources/schema/configuration_space.schema.json` and `src/resources/schema/option.schema.json`. A configuration space is represented by a name and a collection of options. Options have a name, a list of settings ("levels"), and a list of partial orders ("orders"). Each partial order has a "left" element, an "order" element, and a "right" element. Order is one of MST (more sound than or equal to) or MPT (more precise than or equal to). For example, the following option

```
    {
      "name": "optimize",
      "default": "FALSE",
      "levels": [
        "TRUE",
        "FALSE"
      ],
      "orders": [
        {
          "left": "TRUE",
          "order": "MPT",
          "right": "FALSE"
        }
      ]
    }
```

from SOOT's configuration space defines an option, "optimize," with two settings: TRUE and FALSE. The default setting is "FALSE", and the partial orders are that TRUE should be at least as precise as FALSE.

3. Add a new class that inherits from [AbstractCommandLineToolRunner.py](src/ecstatic/runners/AbstractCommandLineToolRunners.py) 
in order to run the tool. Specifically, you must override the `try_run_job` method. If your tool is able to be run relatively simply
(i.e., only by setting command line options), then you might find it easier to 
extend [CommandLineToolRunner.py](src/ecstatic/runners/CommandLineToolRunner.py). See [SOOTRunner.py](src/ecstatic/runners/SOOTRunner.py) 
and [WALARunner.py](src/ecstatic/runners/WALARunner.py) for examples of classes that extend CommandLineToolRunner, and 
[DOOPRunner.py](src/ecstatic/runners/DOOPRunner.py) and [FlowDroidRunner.py](src/ecstatic/runners/FlowDroidRunner.py) for examples of more complex
runners that inherit from AbstractCommandLineToolRunner.py.
4. Add logic to [RunnerFactory.py](src/ecstatic/runners/RunnerFactory.py) to initialize your new runner given the 
name of the tool.
5. Add a new class that inherits from [AbstractRunner.py](src/ecstatic/readers/AbstractReader.py) to read the results of your tool.
The `import_file` method of this class accepts a file name, and returns an iterable of results.
In order to detect violations, it is important that equality be defined correctly between the results.
6. Add logic to [ReaderFactory.py](src/ecstatic/readers/ReaderFactory.py) that will return the appropriate reader given the task and tool name.
7. Depending on how you want to detect violations, you may need to add a new violation checker that inherits from 
[AbstractViolationChecker.py](src/ecstatic/violation_checkers/AbstractViolationChecker.py). The default behavior is 
to just check equality between records. However, if you need to determine ground truths, or you need to filter results 
(as we do in callgraph analyses), then you might need your own class. If you implement a new class, be sure to add logic to
[ViolationCheckerFactory.py](src/ecstatic/violation_checkers/ViolationCheckerFactory.py).
8. That's it!

## Extending with New Input Programs
Adding a new benchmark is relatively simple.
1. Add a new folder to [src/resources/benchmarks](src/resources/benchmarks), with the name of your benchmark.
2. In that folder, create a `build.sh` script that will pull the benchmark code, build it, and put it under 
`/benchmarks/<benchmark_name>` in the Docker container. Add an `index.json` file specifying the programs you want to 
run. The resolver for this file will automatically resolve paths so long as they are unique in the `/benchmarks`
directory.  
