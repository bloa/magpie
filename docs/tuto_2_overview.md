# Overview

## Usage Philosophy

Magpie's source code is entirely self-contained in a single directory ("magpie").
This directory contains a magic `__main__.py` Python file and thus is directly executable.
Therefore, simply running `python3 magpie` from a terminal (in the parent directory) will provide you with a list of possible entry points:

```
usage: python3 magpie ((magpie/){bin,utils}/)TARGET(.py) [ARGS]...
possible TARGET:
    ablation_analysis	(magpie/bin/ablation_analysis.py)
    genetic_programming	(magpie/bin/genetic_programming.py)
    local_search    	(magpie/bin/local_search.py)
    minify_patch    	(magpie/bin/minify_patch.py)
    revalidate_patch	(magpie/bin/revalidate_patch.py)
    show_locations  	(magpie/bin/show_locations.py)
    show_patch      	(magpie/bin/show_patch.py)
    clear_xml       	(magpie/utils/clear_xml.py)
    line_to_xml     	(magpie/utils/line_to_xml.py)
    python_to_xml   	(magpie/utils/python_to_xml.py)
```

To use Magpie, you typically need to provide a _scenario file_ describing, within many other things, where the target software is located, how it is used, how it should be modelled, and what is the fitness function to optimise.
Upon execution Magpie will create two directories, `_magpie_logs` and `_magpie_work`, respectively containing execution log files and temporary software variants.
These two directories may quickly fill up space and can safely be deleted.

Ultimately, the typical Magpie setup will involve the following structure:

    .
    ├── code // Software to optimise
    │   └── ...
    ├── magpie // Magpie source code (not the entire git repository)
    │   └── ...
    ├── _magpie_logs // Experiments' log files (automatically generated)
    │   └── ...
    ├── _magpie_work // Temporary software variants (automatically generated)
    │   └── ...
    └── scenario.txt // Experiments' setup file


# Software Evaluation

Fitness assessment is broken down in five successive steps: "init", "setup", "compile", "test", and "run".

In all but one case (the test step when using the "repair" fitness function), a software variant is immediately discarded it any of the step fails (i.e., if any of the provided command returns a nonzero return code).


## Init

This step is only conducted **once**, at the very beginning of the Mapgie execution.
It is meant to fetch or update software files that wouldn't otherwise be present in the specified directory.
Since it might modify or initialise from scratch target files (e.g., by automatically computing XML ASTs), this step will **always** be performed.

See for example the `examples/scenario/magpie_coverage.txt` scenario in which this step is used to sync a copy of Magpie itself.


## Setup

This step is only conducted **once**, during warmup with the unmodified software, in the original software directory (or in an intermediate copy if the `local_original_copy` option is used).
It is useful for performing some initial processing or compilation so as to avoid wasting resources on things that would otherwise be repeated for every single software variant.
Conversely to the "init" step, this step will not be performed when no evaluation of the target software is required.

See for example the `examples/scenario/triangle-cpp_runtime.txt` scenario in which this step is used to create an initialised CMake build directory.


## Compile

This step is conducted **for every software variant**, before the test and run steps.
It is meant for processing shared between the test and run steps (e.g., compilation).

See for example the `examples/scenario/triangle-c_runtime.txt` and `examples/scenario/triangle-java_repair.txt` scenario in which this step is used to call `make` and `javac`, respectively.


## Test

This step is conducted **for every software variant**, between the compile and run steps.
Whilst technically not absolutely necessary (as it merged with either the compile or run step), it is provided for convenience and quality of life.

This step has three particularities:

  1. Similarly to the run step, when Magpie is processing a configuration file the resulting configuration string is appended at the end of the test command.
  2. When the "repair" or "bloat" fitness function is used, the fitness value is computed immediately and the run command is skipped.
  3. This is only time a command may yield a nonzero return code.


## Run

This step is conducted last, and is used to compute the fitness value in most cases.

If multiple training instances are specified, this step is performed multiple times on a sample of instances in a fashion similar to machine learning's _batch processing_.
The fitness value of the software variant is then aggregated from its multiple individual runs and the different instances.


# Reading Magpie's output

We will use the following example:

    python3 magpie.py local_search --scenario examples/scenario/triangle-cpp_runtime.txt

Execution starts with a "warmup" step.

    ==== WARMUP ====
    WARM    SUCCESS               0.0844                  
    WARM    SUCCESS               0.085                   
    WARM    SUCCESS               0.0843                  
    INITIAL SUCCESS               0.0843                  

Magpie will evaluate multiple times the original software fitness score (default: four times) in order to set the base fitness to improve (default: last fitness).
This step ensures that the all fitness values are fairly compared, as the first few values may exhibit significant variance.

Then, the local search starts.

    ==== START ====
    ... (lines eluded for clarity) ...
    69      COMPILE_CODE_ERROR    None  [5 edit(s)]       
    70      SUCCESS              *0.0107 (12.69%) [5 edit(s)] 
    71      SUCCESS               0.0199 (23.61%) [4 edit(s)] 
    72      SUCCESS               0.0174 (20.64%) [4 edit(s)] 
    73      SUCCESS               0.0147 (17.44%) [4 edit(s)] 
    74      COMPILE_CODE_ERROR    None  [6 edit(s)]       
    75      SUCCESS               0.0793 (94.07%) [4 edit(s)] 
    76      SUCCESS              +0.0107 (12.69%) [6 edit(s)] 
    77      SUCCESS              +0.0107 (12.69%) [5 edit(s)] 
    78      TEST_CODE_ERROR       None  [6 edit(s)]       
    ... (lines eluded for clarity) ...
    98      SUCCESS               0.0199 (23.61%) [6 edit(s)] 
    99      COMPILE_CODE_ERROR    None  [6 edit(s)]       
    100     TEST_CODE_ERROR       None  [6 edit(s)]       
    ==== END ====
    Reason: step budget

For each evaluation Magpie reports the evaluation id, the final status of the mutated software execution, the fitness value, and finally some optional comment (here, the size of the patch).

Few evaluation statuses are then possible.
Note that error statuses (i.e., all except SUCCESS) will always contain the name of the step in which the error arose.

- **CLI_ERROR**: Magpie failed to run the given command
- **CODE_ERROR**: the execution yielded a nonzero return code, indicating some failure
- **TIMEOUT**: the command was interrupted after a given time threshold was reached
- **LENGTHOUT**: the command was interrupted after yielding more output than expected
- **PARSE_ERROR**: Magpie failed to read the expected output
- **SUCCESS**: the execution completed successfully, resulting in a valid fitness value

Fitness values are given both directly and in percentage relatively to the initial fitness.
Values below 100% correspond here to faster variants, while values over 100% correspond to slower ones (note that the status is still `SUCCESS` and not, e.g., `RUNTIME_ERROR`, because the variant is still semantically sound).
An asterisk (`*`) indicates that a new best fitness values have been found, whilst a plus sign (`+`) indicates repeated best values.

At the end of the search Magpie will show the stopping criteria reached: here the 100 steps have completed.
Other possible criteria include for example a target fitness value, or a manual interruption (`C-c`).

Finally, Magpie reports on its execution and eventually details the found improved software variant.
Note that a much more detailed log can be found in the `_magpie_logs` folder.
For convenience, if an improving patch is found, both a patch and a diff file will also be available.

    ==== REPORT ====
    Termination: step budget
    Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-py_slow_1664546789.log
    Patch file: _magpie_logs/triangle-py_slow_1664546789.patch
    Diff file: _magpie_logs/triangle-py_slow_1664546789.diff
    Best fitness: 0.0383
    Best patch: LineDeletion(('triangle.py', 'line', 14)) | LineDeletion(('triangle.py', 'line', 2))
    Diff:
    --- before: triangle.py
    +++ after: triangle.py
    @@ -1,6 +1,5 @@
     import time
     from enum import Enum
    -
    
     class TriangleType(Enum):
         INVALID, EQUILATERAL, ISOCELES, SCALENE = 0, 1, 2, 3
    @@ -12,7 +11,6 @@
    
     def classify_triangle(a, b, c):
    
    -    delay()
    
         # Sort the sides so that a <= b <= c
         if a > b:
