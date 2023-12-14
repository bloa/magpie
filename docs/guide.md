# Usage Philosophy

Magpie's source code is entirely self-contained in the "magpie" folder, whilst the "bin" folder contains Magpie's default entry points.
Entry points will expect a description of the experimental setup provided by a [scenario file](./config.md).
Upon execution, Magpie will create two other folders: "_magpie_logs", that will contain all log files (outputs, patches, diffs, etc) created by Magpie, as well as "_magpie_work", that will contain the temporary software variants.

The typical Magpie setup will then look as follows:

    .
    ├── bin // Default or user-provided entry points
    │   └── ...
    ├── code // Software to optimise
    │   └── ...
    ├── magpie // Magpie source code (not the entire git repository)
    │   └── ...
    ├── magpie.py // Optional main entry point
    │   └── ...
    ├── _magpie_logs // Experiments' log files (automatically generated)
    │   └── ...
    ├── _magpie_work // Temporary software variants (automatically generated)
    │   └── ...
    └── scenario.txt // Experiments' setup file

We provide examples of source code and scenarios in the "example" folder.


# Software Evaluation

Fitness assessment is broken down in five successive steps: "init", "setup", "compile", "test", and "run".

In all but one case (the test step when using the "repair" fitness function), a software variant is immediately discarded it any of the step fails (i.e., if any of the provided command returns a nonzero return code).

## Init

This step is only conducted **once**, at the very beginning of the Mapgie execution.
It is meant to fetch or update software files that wouldn't otherwise be present in the specified directory.
Since it might modify or initialise from scratch target files (e.g., by automatically computing XML ASTs), this step will **always** be performed.

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


# Fitness Function

Magpie generic entry points natively support many fitness schemes.

Out-of-the-box:
- **time**: the fitness value is the time taken to execute the run command, as seen from the main Magpie Python process.
- **bloat_lines**, **bloat_words**, **bloat_chars**: Magpie counts the number of lines, words, or character of every targeted file.

Require specific outputs:
- **repair**: during the test step, Magpie checks STDOUT for a specific strings (e.g., `Tests run: XXX` and `Failures: XXX` to support JUnit) and computes the percentage of failing tests.
  Note that we need the total number of tests to avoid some fairy situations (e.g., the test harness crashing and only reporting the first, and therefore only, test fail).
  Magpie is currently compatible with JUnit (Java), pytest (Python), and minitest (Ruby).
- **posix_time**: STDERR is checked for a string matching `real XXX`.
  This can easily be achieved by preceding the vanilla command with, e.g. on most Linux distributions, `/usr/bin/time -p `.
  Note that the GNU time command is not very precise.
- **perf_time**: STDERR is checked for a string matching `XXX seconds time elapsed`.
  This can easily be achieved by preceding the vanilla command with, e.g. , `perf stat `.
- **perf_instructions**: STDERR is checked for a string matching `XXX instructions` (commas thousands separators are ignored).
  Again, this can easily be achieved by preceding the vanilla command with, e.g. on most Linux distributions, `perf stat `.
- **output**: Magpie checks STDOUT for the generic `MAGPIE_FITNESS: XXX` string.


# Reading Magpie's output

We will use the following example:

    ./magpie.py local_search --scenario examples/scenario/triangle-cpp_runtime.txt

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


# Entry Points

    bin
    ├── ablation_analysis.py
    ├── genetic_programming.py
    ├── local_search.py
    ├── minify_patch.py
    ├── revalidate.py
    ├── show_locations.py
    └── show_patch.py

There are multiple ways to use these entry points.
Because they are located in a sub-folder and not at top-level, they must be loaded as modules using the `-m` option of the Python interpreter.

    python3 -m bin.local_search --scenario examples/scenario/triangle-cpp_runtime.txt

For maximum convenience, we provide the `magpie.py` script that also accept the equivalent commands:

    python3 magpie.py bin/local_search.py --scenario examples/scenario/triangle-cpp_runtime.txt
<!-- -->
    python3 magpie.py bin/local_search --scenario examples/scenario/triangle-cpp_runtime.txt
<!-- -->
    python3 magpie.py local_search.py --scenario examples/scenario/triangle-cpp_runtime.txt
<!-- -->
    python3 magpie.py local_search --scenario examples/scenario/triangle-cpp_runtime.txt
<!-- -->
    ./magpie.py local_search --scenario examples/scenario/triangle-cpp_runtime.txt

Alternatively, these entry points (as any custom-written ones) can be moved at top-level and run from there:

    mv bin/local_search.py .
    python3 local_search.py --scenario examples/scenario/triangle-cpp_runtime.txt
<!-- -->
    mv bin/local_search.py .
    ./local_search.py --scenario examples/scenario/triangle-cpp_runtime.txt


Note on requirements of "triangle_XXX" scenario:
- the Python scenario require Python 3.7+ and [pytest](https://docs.pytest.org).
- the Ruby scenario requires Ruby and [minitest](https://docs.seattlerb.org/minitest/).
- the Java scenario only requires Java, as both jUnit and the SrcML file are already provided.
- the C scenario require make.
- the C++ scenario require CMake.


## Local Search

Examples:

    ./magpie.py local_search --scenario examples/scenario/triangle-cpp_runtime.txt
<!-- -->
    ./magpie.py local_search --scenario examples/scenario/triangle-java_repair.txt
<!-- -->
    ./magpie.py local_search --scenario examples/scenario/triangle-rb_repair.txt
<!-- -->
    ./magpie.py local_search --scenario examples/scenario/triangle-py_bloat.txt

Note: whilst the `--seed` option enables setting the initial random seed, which may lead to reproducible results in cases in which the fitness function is deterministic (bloat is fine, repair *may* be, but running time measurements are usually too noisy).


## Show Patch

The `show_patch.py` utility provides a way to quickly (without evaluation) apply a Magpie patch and show the resulting diff.
A patch can either be provided directly or as a path to a file containing the patch representation.

Examples:

    ./magpie.py show_patch --scenario examples/scenario/triangle-cpp_runtime.txt --patch "StmtDeletion(('triangle.cpp.xml', 'stmt', 3))"
<!-- -->
    ./magpie.py show_patch --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"

In addition, using the `--keep` option will also instruct Magpie to leave a copy of the mutated software for further manual investigation.


## Show Locations from Software

The `show_location.py` utility provides a way to quickly verify which location points are defined for a given software.
The `--filename` and `--type` options allow for specifying a specific subset of locations; by default all locations of all targeted files are showed.

Examples:

    ./magpie.py show_locations --scenario examples/scenario/triangle-rb_repair.txt
<!-- -->
    ./magpie.py show_locations --scenario examples/scenario/triangle-rb_repair.txt --filename triangle.rb --type line


## Revalidate Patch

The `revalidate_patch.py` entry point allows for quickly assessing the fitness of a given patch.
A patch can either be provided directly or as a path to a file containing the patch representation.

Examples:

    ./magpie.py revalidate_patch --scenario examples/scenario/triangle-cpp_runtime.txt --patch "StmtReplacement(('triangle.cpp.xml', 'stmt', 3), ('triangle.cpp.xml', 'stmt', 12))"
<!-- -->
    ./magpie.py revalidate_patch --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"


## Minify Patch

The patches generated by Magpie are seldom optimal and often contain bloat.
The `minify_patch.py` entry point processes the individual mutations of a given patch in order to obtain a leaner, cleaner, shorter, and more reliable patch.
A patch can either be provided directly or as a path to a file containing the patch representation.

In practice, every individual edit is separately evaluated and ranked, and a new patch is constructed by reintroducing every edit in order, only accepting it on fitness improvement.
This new patch (or the original, in rare cases in which the rebuild is unsuccessful) is then made as small as possible by trying to remove every edit one by one.

Example:

    ./magpie.py minify_patch --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"

Note that noise in fitness measurement may lead to non-optimal patch being returned.


## Ablation Analysis

In contrary to the `minify_patch.py` entry point, which aims to minimise patch size, the `ablation_analysis.py` entry point aims to highlight the individual contribution of every edit in the overall fitness improvement.
A patch can either be provided directly or as a path to a file containing the patch representation.

Example:

    ./magpie.py ablation_analysis --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"


## Miscellaneous

### Line to XML Converter

Example:

    python3 utils/line_to_xml.py --file examples/code/triangle-java_slow/Triangle.java


### Python to AST XML Converter

Examples:

    python3 utils/python_to_xml.py examples/code/triangle-py_bug/triangle.py
<!-- -->
    cat examples/code/triangle-py_bug/triangle.py | python3 utils/python_to_xml.py


### AST XML to Source Code Converter

Examples:

    python3 utils/clear_xml.py examples/code/triangle-py_slow/triangle.py.xml
<!-- -->
    cat examples/code/triangle-py_bug/triangle.py | python3 utils/python_to_xml.py | python3 utils/clear_xml.py
