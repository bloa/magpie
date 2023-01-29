# Basic Usage

We provide few generic entry points for optimisation/learning/training.

    bin
    ├── ablation_analysis.py
    ├── genetic_programming.py
    ├── local_search.py
    ├── minify_patch.py
    ├── revalidate.py
    ├── show_locations.py
    └── show_patch.py

Because they are located in a sub-folder and not at top-level, they require a little bit of Python magic speech (e.g., `python3 -m bin.local_search` instead of `python3 magpie_runtime.py`).
They can, however, be moved at top-level without any modification to simplify usage if so desired.

Note that for the sake of genericity, these scripts are limited in the granularity level (no AST node) and fitness functions they provide.

There are multiple ways to use these entry points.
Because they are located in a sub-folder and not at top-level, they must be loaded as modules using the `-m` option of the Python interpreter.
For example:
    python3 -m bin.local_search --scenario examples/scenario/triangle-cpp_runtime.txt

For maximum convenience, we provide the `magpie.py` script that also accept the equivalent commands:
    python3 magpie.py bin/local_search.py --scenario examples/scenario/triangle-cpp_runtime.txt
    python3 magpie.py bin/local_search --scenario examples/scenario/triangle-cpp_runtime.txt
    python3 magpie.py local_search.py --scenario examples/scenario/triangle-cpp_runtime.txt
    python3 magpie.py local_search --scenario examples/scenario/triangle-cpp_runtime.txt
    ./magpie.py local_search --scenario examples/scenario/triangle-cpp_runtime.txt

Alternatively, these entry points (as any custom-written ones) can be moved at top-level and run from there:
    mv bin/local_search.py .
    ./local_search.py --scenario examples/scenario/triangle-cpp_runtime.txt


## Software Evaluation

In the generic entry points software fitness assessment is broken down in four successive steps: "setup", "compile", "test", and "run".

In all but one case (the test step when using the "repair" fitness function), a software variant is immediately discarded it any of the step fails (i.e., if any of the provided command returns a nonzero return code).

### Setup

This step is only conducted **once**, during warmup with the unmodified software, in the original software directory (or in an intermediate copy if the `local_original_copy` option is used).
It is useful for performing some initial processing or compilation so as to avoid wasting resources on things that would otherwise be repeated for every single software variant.

See for example the `examples/scenario/triangle-cpp_runtime.txt` scenario in which this step is used to create an initialised CMake build directory.

### Compile

This step is conducted **for every software variant**, before the test and run steps.
It is meant for processing shared between the test and run steps (e.g., compilation).

See for example the `examples/scenario/triangle-c_runtime.txt` and `examples/scenario/triangle-java_repair.txt` scenario in which this step is used to call `make` and `javac`, respectively.

### Test

This step is conducted **for every software variant**, between the compile and run steps.
Whilst technically not absolutely necessary (as it merged with either the compile or run step), it is provided for convenience and quality of life.

This step has three particularities:
1. Similarly to the run step, when Magpie is processing a configuration file the resulting configuration string is appended at the end of the test command.
2. When the "repair" or "bloat" fitness function is used, the fitness value is computed immediately and the run command is skipped.
3. This is only time a command may yield a nonzero return code.

### Run

This step is conducted last, and is used to compute the fitness value in most cases.


## Fitness Function

Magpie generic entry points natively support many fitness schemes.

Out-of-the-box:
- **time**: the fitness value is the time taken to execute the run command, as seen from the main Magpie Python process.
- **bloat_lines**, **bloat_words**, **bloat_chars**: Magpie counts the number of lines, words, or character of every targeted file.

Require specific outputs:
- **repair**: during the test step, Magpie checks STDOUT for a string matching `XXX fail` or `XXX error`, "XXX" being the number of bugs to repair; if no such string is found, then a string matching "XXX pass" must be present instead (resulting in a fitness value of 0).  
  This scheme should at least be compatible with JUnit (Java), pytest (Python), and minitest (Ruby).
- **posix_time**: STDERR is checked for a string matching `real XXX`.
  This can easily be achieved by preceding the vanilla command with, e.g. on most Linux distributions, `/usr/bin/time -p `.
  Note that the GNU time command is not very precise.
- **perf_time**: STDERR is checked for a string matching `XXX seconds time elapsed`.
  This can easily be achieved by preceding the vanilla command with, e.g. , `perf stat `.
- **perf_instructions**: STDERR is checked for a string matching `XXX instructions` (commas thousands separators are ignored).
  Again, this can easily be achieved by preceding the vanilla command with, e.g. on most Linux distributions, `perf stat `.
- **output**: Magpie checks STDOUT for the generic `MAGPIE_FITNESS: XXX` string.


## Reading Magpie's output

First we look at the output of the running time minimisation example.

    ==== WARMUP ====
    WARM    SUCCESS               0.0844                  
    WARM    SUCCESS               0.085                   
    WARM    SUCCESS               0.0843                  
    INITIAL SUCCESS               0.0843                  

First, Magpie will evaluate multiple times the original software fitness score (default: four times) in order to set the base fitness to improve.
This warming up step ensures that the all fitness values are fairly compared, as the first few values may exhibit significant variance.

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

Then, Magpie will use the chosen evolutionary algorithm to modify the original software.
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

Finally, Magpie will show the stopping criteria reached: here the 100 steps have completed.
Other possible criteria include for example a target fitness value, or a manual interruption (`C-c`).

    ==== REPORT ====
    Termination: step budget
    Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-py_slow_1664546789.log
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

Finally, Magpie reports on its execution and eventually details the found improved software variant.
Note that a much more detailed log is also stored in the `_magpie_logs` folder.


# Entry Points

Note on requirements of "triangle_XXX" scenario:
- the Python triangles scenario require Python 3.7+ and [`pytest`](https://docs.pytest.org).
- the Ruby scenario requires Ruby and [`minitest`](https://docs.seattlerb.org/minitest/).
- the Java scenario only requires Java, as both `junit` and the SrcML file are already provided.
- the C scenario require make.
- the C++ scenario require CMake.


## Local Search

Examples:

    python3 -m bin.local_search --scenario examples/scenario/triangle-cpp_runtime.txt
    python3 -m bin.local_search --scenario examples/scenario/triangle-java_repair.txt
    python3 -m bin.local_search --scenario examples/scenario/triangle-rb_repair.txt
    python3 -m bin.local_search --scenario examples/scenario/triangle-py_bloat.txt

Note: whilst the `--seed` option enables setting the initial random seed, which may lead to reproducible results in cases in which the fitness function is deterministic (bloat is fine, repair *may* be, but usually running time measurements are too noisy).


## Show Patch

The `show_patch.py` utility provides a way to quickly (without evaluation) apply a Magpie patch and show the resulting diff.
A patch can either be provided directly or as a path to a file containing the patch representation.

Examples:

    python3 -m bin.show_patch --scenario examples/scenario/triangle-cpp_runtime.txt --patch "LineDeletion(('triangle.cpp', 'line', 10))"
    python3 -m bin.show_patch --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"

In addition, using the `--keep` option will also instruct Magpie to leave a copy of the mutated software for further manual investigation.


## Show Locations from Software

The `show_location.py` utility provides a way to quickly verify which location points are defined for a given software.
The `--filename` and `--type` options allow for specifying a specific subset of locations; by default all locations of all targeted files are showed.

Examples:

    python3 -m bin.show_locations --scenario examples/scenario/triangle-rb_repair.txt
    python3 -m bin.show_locations --scenario examples/scenario/triangle-rb_repair.txt --filename triangle.rb --type line


## Revalidate Patch

The `revalidate_patch.py` entry point allows for quickly assessing the fitness of a given patch.
A patch can either be provided directly or as a path to a file containing the patch representation.

Examples:

    python3 -m bin.revalidate_patch --scenario examples/scenario/triangle-cpp_runtime.txt --patch "LineDeletion(('triangle.cpp', 'line', 10))"
    python3 -m bin.revalidate_patch --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"


## Minify Patch

The patches generated by Magpie are seldom optimal and often contain bloat.
The `minify_patch.py` entry point processes the individual mutations of a given patch in order to obtain a leaner, cleaner, shorter, and more reliable patch.
A patch can either be provided directly or as a path to a file containing the patch representation.

In practice, every individual edit is separately evaluated and ranked, and a new patch is constructed by reintroducing every edit in order, only accepting it on fitness improvement.
This new patch (or the original, in rare cases in which the rebuild is unsuccessful) is then made as small as possible by trying to remove every edit one by one.

Example:

    python3 -m bin.minify_patch --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"

Note that noise in fitness measurement may lead to non-optimal patch being returned.


## Ablation Analysis

In contrary to the `minify_patch.py` entry point, which aims to minimise patch size, the `ablation_analysis.py` entry point aims to highlight the individual contribution of every edit in the overall fitness improvement.
A patch can either be provided directly or as a path to a file containing the patch representation.

Example:

    python3 -m bin.ablation_analysis --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"


## Misc Utilities

### Line to XML Converter

Example:

    python3 bin/line_xml.py --file examples/code/triangle-java_slow/Triangle.java


# Real World Example

First, download and extract Minisat 2.2.0 (as the real-world target software)
For consistency we extract it here in `example/code`, beside the provided example toy software.

    wget "http://minisat.se/downloads/minisat-2.2.0.tar.gz"
    tar xzf minisat-2.2.0.tar.gz -C example/code
    rm minisat-2.2.0.tar.gz

Then setup the MiniSAT directory with files used by Magpie.

    patch -d examples/code/minisat -p 1 < examples/code/minisat_setup/minisat.patch
    cp examples/code/minisat_setup/data examples/code/minisat
    cp examples/code/minisat_setup/*.sh examples/code/minisat
    cp examples/code/minisat_setup/Solver.cc.xml examples/code/minisat/core
    cp examples/code/minisat_setup/minisat*.params examples/code/minisat/core

In particular:

- `minisat.patch` is applied to add comment support to MiniSAT's Dimacs parser
- `data` contains 20 instances from [SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
- `compile.sh` simply runs the MiniSAT-provided makefile
- `test.sh` checks MiniSAT's output on 5 SAT and 5 UNSAT instances
- `run.sh` runs MiniSAT on all 20 instances
- `Solver.cc.xml` contains the AST of the MiniSAT's `core/Solver.cc` file as provided by [SrcML](https://www.srcml.org/).
- `minisat.params` and two variants define the MiniSAT's configuration space

To optimise running time:

    python3 -m bin.magpie_runtime --scenario examples/scenario/minisat_runtime.txt
    python3 -m examples.magpie_runtime_xml --scenario examples/scenario/minisat_runtime_xml.txt

To remove any unnecessary code:

    python3 -m bin.magpie_bloat --scenario examples/scenario/minisat_debloat.txt
    python3 -m examples.magpie_bloat2 --scenario examples/scenario/minisat_debloat.txt

To optimise command line parameters:

    python3 -m bin.magpie_config --scenario examples/scenario/minisat_config.txt
    python3 -m examples.magpie_config_minisat --scenario examples/scenario/minisat_config_advanced.txt
