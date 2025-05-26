# Basic Usage

This tutorial walks through three common use cases of Magpie, demonstrating its core functionality.
By the end, you'll understand how to:
1. **optimise software** by searching for performance-improving patches,
2. **fix bugs** by generating functional patches, and
3. **inspect and analyse** Magpie-generated patches.

Each section provides step-by-step instructions, example command lines, and expected outcomes.


## Use Case 1: Finding a Patch to Improve Execution Time

Optimising software performance is a key use case for Magpie.
In this section, we demonstrate how to use Magpie to search for patches that improve execution time.


### Target software

We use the very simple `examples/triangle-c` example as target software.
There are four core files of interest.
- `triangle.c` contains the software implementation;
- `test_triangle.c` contains the software test suite;
- `run_triangle.c` contains the benchmark against which we assess performance;
- `makefile` contains the compilation pipeline.


### Scenario file

We use the scenario described in the `examples/triangle-c/_magpie/scenario_slow.txt` file.

```
[software]
path = examples/triangle-c
target_files =
    triangle.c.xml
fitness = time
```
The first section describes the software under optimisation.
- **path**: the location of the software. This folder is duplicated to generate and evaluate variants of the original software.
- **target_files**: the list of the files Magpie can modify. Here, a single XML file (derived from `triangle.c`, as explained below)
- **fitness**: the performance metric used to evaluate changes. Here, execution time measured via a Python wall-clock timer.

```
init_cmd = bash init_slow.sh
compile_cmd = make test_triangle run_triangle
test_cmd = ./test_triangle
run_cmd = ./run_triangle
run_timeout = 1
```
This next section defines how software variants are evaluated.
- **init_cmd** is a script run once before the search starts; it introduces an artificial delay in `triangle.c` (which Magpie will try to remove), and provides a XML representation it's AST;
- **compile_cmd** use _make_ to build the test suite and benchmark executables;
- **test_cmd** runs the test suite to ensure correctness;
- **run_cmd** runs the benchmark to measure execution time; and finally
- **run_timeout** limits benchmark execution to 1 second to prevent excessive runtime for slow variants.

```
[search]
max_steps = 100
max_time = 60
possible_edits =
    XmlNodeDeletion<stmt>
    XmlNodeReplacement<stmt>
    XmlNodeInsertion<stmt,block>
```
Finally, this section configures Magpie's search process.
- **max_steps** adds a limit on the number of patches generated;
- **max_time** adds a limit on the duration of the search process (in seconds); and
- **possible_edits** describes the set of modifications Magpie can apply:
  - `XmlNodeDeletion<stmt>` removes an `<stmt>` subtree from the XML AST;
  - `XmlNodeReplacement<stmt>` replaces an `<stmt>` subtree with another from the original AST;
  - `XmlNodeInsertion<stmt,block>` inserts an `<stmt>` subtree inside an existing `<block>` node.


### Search process

Magpie offers two entry points to generate software variants: **local_search** and **genetic_programming**.

    python3 magpie local_search --scenario examples/triangle-c/_magpie/scenario_slow.txt
<!-- -->
    python3 magpie genetic_programming --scenario examples/triangle-c/_magpie/scenario_slow.txt

We will focus on local search.

**Initial evaluation**

```
==== SEARCH: FirstImprovement ====
~~~~ WARMUP ~~~~
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
REF     SUCCESS               0.08 (--) [0 edit(s)]
```

Magpie begins by evaluating the original software three times to establish a baseline execution time.
Here, the last recorded measurement (**0.0802 seconds**, as seen in the log file) is used as the reference.

**Generating software variants**

```
~~~~ START ~~~~
1       COMPILE_CODE_ERROR    None (--) [1 edit(s)]  
2       TEST_CODE_ERROR       None (--) [1 edit(s)]  
3       SUCCESS               0.08 (101.87%) [1 edit(s)]  
4       TEST_CODE_ERROR       None (--) [1 edit(s)]  
5       SUCCESS              *0.01 (11.85%) [1 edit(s)]
```

Magpie then begins generating and evaluating modified software variants:
- Variant 1 fails to compile (**COMPILE_CODE_ERROR**) and is immediately discarded;
- Variant 2 compiles but fails the test suite (**TEST_CODE_ERROR**) and is also discarded.
- Variant 3 compiles, passes the test suite (**SUCCESS**), but is slightly slower than the reference (0.0817s, or 1.87% slower);
- Variant 5 achieves a significant performance gain, running in roughly 0.01s (only 11.85% of the original execution time); the "*" indicates this is the best solution found so far.

**Caching and reusing results**

```
66      SUCCESS               0.01 (6.98%) [6 edit(s)]  
67      SUCCESS              +0.00 (1.22%) [4 edit(s)] [cached] 
68      SUCCESS               0.01 (11.01%) [3 edit(s)] [cached] 
```

Magpie caches previously evaluated variants to avoid redundant computations:
- Variant 66 introduces a 6-edit patch, leading to a fast but not optimal execution time, it is discarded;
- Variant 67 is a previously tested variant with 4 edits; it shares the best-known execution time (1.22% of the original) and is accept for further evolution;
- Variant 68, with 3 edits, is also recognised as a previously known variant, but is slower and therefore immediately discarded.

**Final report**

Once the search process completes, Magpie summarises the results and provides details about the best patch found.

```
~~~~ END ~~~~

==== REPORT ====
Termination: step budget
Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-c_20250328_1743176048.log
Patch file: _magpie_logs/triangle-c_20250328_1743176048.patch
Diff file: _magpie_logs/triangle-c_20250328_1743176048.diff
Reference fitness: 0.08
Best fitness: 0.00

==== BEST PATCH ====
XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 3)) | XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 4))

==== DIFF ====
--- before: triangle.c
+++ after: triangle.c
@@ -8,14 +8,10 @@
 int classify_triangle(double a, double b, double c) {
   double tmp;
 
-  delay();
+  
 
   // Sort the sides so that a <= b <= c
-  if(a > b) {
-    tmp = a;
-    a = b;
-    b = tmp;
-  }
+  
 
   if(a > c) {
     tmp = a;
```

In this case, Magpie stopped after generating 100 software variants.
It successfully found a patch, essentially entirely eliminating the reference execution time of 0.08 seconds.
The patch contains two edits, `XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 3))` and `XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 4))`.
Looking at the diff, it deletes the call to the delay function as well as removing a redundant sorting of the triangle sides.

The paths to three files are provided:
- `_magpie_logs/{software}_{timestamp}.log` provides a complete and augmented output;
- `_magpie_logs/{software}_{timestamp}.patch` contains the best patch in Magpie's internal representation;
- `_magpie_logs/{software}_{timestamp}.diff` contains the best patch in diff representation.


## Use Case 2: Finding a Patch to Fix a Bug

Automated program repair is another feature of Magpie.
In this section, we demonstrate how Magpie can be used to automatically generate patches that fix bugs in the software, improving its functionality and ensuring it passes the provided test suite.


### Target software

We use the slightly more complex `examples/triangle-cpp` example as target software.
There are also four core files of interest, with similar purposes.
- `triangle.cpp` contains the software implementation;
- `test_triangle.cpp` contains the software test suite;
- `run_triangle.cpp` contains the benchmark against which we assess performance;
- `CMakeLists.txt` contains the compilation pipeline.


### Scenario file

We use the scenario described in the `examples/triangle-cpp/_magpie/scenario_bug.txt` file.

```
[magpie]                              
local_original_copy = True
```
This section instructs Magpie to maintain an intermediary copy of the original software.
This is used here because the first step in the CMake process involves creating and populating a build directory, which is once done during the **setup_cmd** phase.
Having this intermediary copy ensures that the original directory remains unmodified, eliminating the need for cleanup at the end of the search process.

```
[software]
path = examples/triangle-cpp
target_files =
    triangle.cpp.xml
fitness = repair
```
As before, this section describes the software under optimisation: its location, the list of files Magpie can modify, and the selected performance metric.

```
init_cmd = bash init_bug.sh
setup_cmd = bash setup.sh
compile_cmd = bash compile.sh
test_cmd = ./build/test_triangle
run_cmd =
```
Because the goal here is to fix a bug, the performance metric can be computed during the test suite phase, hence no **run_cmd** is specified.

```
[search]
target_fitness = 0
max_steps = 100
possible_edits =
    XmlNodeDeletion<stmt>
    XmlNodeReplacement<stmt>
    XmlNodeInsertion<stmt,block>
```
As before, the search is limited to a maximum of 100 generated variants and 60 seconds.
However, in this case, the search will also stop immediately once a software variant with a fitness value of "at least 0" is found.


### Automated bug fixing

The "repair" fitness function computes the ratio of failed tests to the total number of tests.
In our example test suite, `test_triangle.cpp`, you can see the following:
```
  printf("Tests run: %d\n", passed+failed);
  printf("Failures: %d\n", failed);
```

These two figures are _essential_ to ensure that the software variant doesn’t interfere with the test suite. Without them, there is a risk that the variant might cause the test suite to stop prematurely, ignore tests that should fail, or fail to run tests altogether, which could lead to a false result of no failing test cases.
In the following, Magpie reports an initial fitness value of **33.33**, with a total of 21 test cases, 7 of which are failing.

The "repair" fitness function should provide compatibility with the default output of JUnit (Java), Pytest (Python) and minitest (Ruby).


### Search process

Again, Magpie offers two entry points to generate software variants: local_search and genetic_programming.

    python3 magpie local_search --scenario examples/triangle-cpp/_magpie/scenario_bug.txt
<!-- -->
    python3 magpie genetic_programming --scenario examples/triangle-cpp/_magpie/scenario_bug.txt

This time, we will focus on genetic programming.

**Initial evaluation**

```
==== SEARCH: GeneticProgrammingUniformConcat ====
~~~~ WARMUP ~~~~
WARM    SUCCESS               33.33 (--) [0 edit(s)]  
WARM    SUCCESS               33.33 (--) [0 edit(s)]  
WARM    SUCCESS               33.33 (--) [0 edit(s)]  
REF     SUCCESS               33.33 (--) [0 edit(s)] 
```


**Generating software variants**

```
~~~~ START ~~~~
0-1     SUCCESS              *19.05 (57.16%) [1 edit(s)]  
0-2     SUCCESS               33.33 (100.00%) [1 edit(s)]  
0-3     SUCCESS               33.33 (100.00%) [1 edit(s)]  
0-4     SUCCESS               61.90 (185.72%) [1 edit(s)]  
0-5     SUCCESS               19.05 (57.16%) [1 edit(s)]  
0-6     SUCCESS               47.62 (142.87%) [1 edit(s)]  
0-7     SUCCESS               71.43 (214.31%) [1 edit(s)]  
0-8     SUCCESS               33.33 (100.00%) [1 edit(s)]  
0-9     SUCCESS               42.86 (128.59%) [1 edit(s)]  
0-10    COMPILE_CODE_ERROR    None (--) [1 edit(s)]  
REF     SUCCESS               33.33 (--) [0 edit(s)] [cached] 
BEST    SUCCESS              *19.05 (57.16%) [1 edit(s)] [cached]
```

Genetic programming operates on a population of software variants.
The initial population consists of variants containing a single edit each.
At the end of every generation, both the initial and best variants are revisited (often appearing as cached results);
this ensures that any changes to the benchmark or test suite since the previous generation are accounted for.


**Final report**

```
==== REPORT ====
Termination: step budget
Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-cpp_20250328_1743183012.log
Patch file: _magpie_logs/triangle-cpp_20250328_1743183012.patch
Diff file: _magpie_logs/triangle-cpp_20250328_1743183012.diff
Reference fitness: 33.33
Best fitness: 19.05

==== BEST PATCH ====
XmlNodeReplacement<stmt>(('triangle.cpp.xml', 'stmt', 16), ('triangle.cpp.xml', 'stmt', 18))

==== DIFF ====
--- before: triangle.cpp
+++ after: triangle.cpp
@@ -28,7 +28,7 @@
   }/*auto*/
   if(a == b && b == c)/*auto*/{
    
-    return ISOSCELES;
+    return EQUILATERAL;
   }/*auto*/ // TODO: fixme
   if(a == b || b == c)/*auto*/{
```

Magpie will report partial fixes as long as some failing test cases have been addressed.
Here, out of the 7 initial failing test cases, only 3 remain.


## Use Case 3: Working with Magpie-generated patches

In this section, we explore how to manipulate and analyse patches generated by Magpie.
This includes:
- **recomputing a diff** to compare modified and original code,
- **re-evaluating the fitness value** such as execution time, test case outcomes, etc,
- **simplifying a patch** by removing unnecessary modifications,
- **performing ablation analysis** to assess the impact of individual changes.

The following examples demonstrate these operations using patches provided directly via the command line.
However, note that Magpie’s entry points also accept patch files via the `--patch` argument, allowing you to work directly with paths provided in its final reports.


### Recomputing a diff

To inspect a patch without applying it, use the `show_patch` entry point:

    python3 magpie show_patch --scenario examples/triangle-cpp/_magpie/scenario_bug.txt --patch "XmlNodeReplacement<stmt>(('triangle.cpp.xml', 'stmt', 16), ('triangle.cpp.xml', 'stmt', 18))"

To generate a modified version of the software on disk, add `--keep`.
The path to the variant will be shown after "Artefact" in the output.

    python3 magpie show_patch --scenario examples/triangle-cpp/_magpie/scenario_bug.txt --patch "XmlNodeReplacement<stmt>(('triangle.cpp.xml', 'stmt', 16), ('triangle.cpp.xml', 'stmt', 18))" --keep

```
==== REPORT ====
Patch: XmlNodeReplacement<stmt>(('triangle.cpp.xml', 'stmt', 16), ('triangle.cpp.xml', 'stmt', 18))
Artefact: /home/aymeric/git/magpie/_magpie_work/triangle-cpp_20250331_1743429554
Diff:
--- before: triangle.cpp
+++ after: triangle.cpp
@@ -28,7 +28,7 @@
   }/*auto*/
   if(a == b && b == c)/*auto*/{
    
-    return ISOSCELES;
+    return EQUILATERAL;
   }/*auto*/ // TODO: fixme
   if(a == b || b == c)/*auto*/{
```


### Recomputing the fitness value

Similarly, to reassess the fitness value of a particular patch, use the `revalidate_patch` entry point:

    python3 magpie revalidate_patch --scenario examples/triangle-cpp/_magpie/scenario_bug.txt --patch "XmlNodeReplacement<stmt>(('triangle.cpp.xml', 'stmt', 16), ('triangle.cpp.xml', 'stmt', 18))"


### Simplifying a patch

The `minify_patch` entry point breaks the user-provided patch into individual edits, then reconstructs a more efficient version by removing any that do not contribute positively:

    python3 magpie minify_patch --scenario examples/triangle-c/_magpie/scenario_slow.txt --patch "XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 3)) | XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 4))"

```
==== SEARCH: ValidMinify ====
~~~~ WARMUP ~~~~
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
REF     SUCCESS               0.08 (--) [0 edit(s)]  

~~~~ START ~~~~
---- cleanup ----
---- initial patch ----
1       SUCCESS              *0.00 (5.92%) [2 edit(s)]  
---- ranking ----
2       SUCCESS               0.01 (11.96%) [1 edit(s)]  
3       SUCCESS               0.08 (101.89%) [1 edit(s)]  
---- rebuild ----
4       SUCCESS              +0.00 (5.92%) [2 edit(s)] [cached] 
---- simplify ----
5       SUCCESS               0.08 (101.89%) [1 edit(s)] [cached] 
6       SUCCESS               0.01 (11.96%) [1 edit(s)] [cached] 
~~~~ END ~~~~


==== REPORT ====
Termination: validation end
Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-c_20250331_1743431029.log
Patch file: _magpie_logs/triangle-c_20250331_1743431029.patch
Diff file: _magpie_logs/triangle-c_20250331_1743431029.diff
Reference fitness: 0.0797
Best fitness: 0.0090

==== BEST PATCH ====
XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 3)) | XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 4))

==== DIFF ====
--- before: triangle.c
+++ after: triangle.c
@@ -8,14 +8,10 @@
 int classify_triangle(double a, double b, double c) {
   double tmp;
 
-  delay();
+  
 
   // Sort the sides so that a <= b <= c
-  if(a > b) {
-    tmp = a;
-    a = b;
-    b = tmp;
-  }
+  
 
   if(a > c) {
     tmp = a;

```

Note that due to measurement noise (e.g., execution time), this procedure may not always yield the smallest possible patch.


### Analysing a patch

Finally, the `ablation_analysis` entry point starts from a given patch and iteratively removes the least contributing edit.
It then lists all intermediary patches in reverse order with their fitness values, helping to identify which edits are truly necessary.

    python3 magpie ablation_analysis --scenario examples/triangle-c/_magpie/scenario_slow.txt --patch "XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 3)) | XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 4))"

```
==== SEARCH: AblationAnalysis ====
~~~~ WARMUP ~~~~
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
WARM    SUCCESS               0.08 (--) [0 edit(s)]  
REF     SUCCESS               0.08 (--) [0 edit(s)]  

~~~~ START ~~~~
---- cleanup ----
---- exploration ----
1       SUCCESS              *0.01 (8.47%) [2 edit(s)]  
2       SUCCESS               0.08 (105.56%) [1 edit(s)]  
3       SUCCESS               0.01 (11.64%) [1 edit(s)]  
4       SUCCESS               0.08 (100.00%) [0 edit(s)] [cached] 
---- backtrack ----
5       SUCCESS              +0.01 (8.47%) [2 edit(s)] [cached] 
6       SUCCESS               0.01 (11.64%) [1 edit(s)] [cached] removing XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 4))
7       SUCCESS               0.08 (100.00%) [0 edit(s)] [cached] removing XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 3))
~~~~ END ~~~~

==== REPORT ====
Termination: ablation end
Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-c_20250331_1743431229.log
Patch file: _magpie_logs/triangle-c_20250331_1743431229.patch
Diff file: _magpie_logs/triangle-c_20250331_1743431229.diff
Reference fitness: 0.08
Best fitness: 0.01

==== BEST PATCH ====
XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 3)) | XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 4))

==== DIFF ====
--- before: triangle.c
+++ after: triangle.c
@@ -8,14 +8,10 @@
 int classify_triangle(double a, double b, double c) {
   double tmp;
 
-  delay();
+  
 
   // Sort the sides so that a <= b <= c
-  if(a > b) {
-    tmp = a;
-    a = b;
-    b = tmp;
-  }
+  
 
   if(a > c) {
     tmp = a;

```

Here Magpie shows that the `XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 3))` edit accounts for 88.36% running time improvement, whilst `XmlNodeDeletion<stmt>(('triangle.c.xml', 'stmt', 4))` only accounts for the additional 3.17%.
