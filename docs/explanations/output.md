# Reading Magpie's output

To understand Magpie's output, we'll use the following example command:

    python3 magpie local_search --scenario examples/triangle-cpp/_magpie/scenario_slow.txt


## Warmup

Execution begins by evaluating the fitness of the original, unmodified software:

```
==== SEARCH: FirstImprovement ====
~~~~ WARMUP ~~~~
WARM    SUCCESS               0.0823 (--) [0 edit(s)]  
WARM    SUCCESS               0.0811 (--) [0 edit(s)]  
WARM    SUCCESS               0.0765 (--) [0 edit(s)]  
REF     SUCCESS               0.0765 (--) [0 edit(s)]
```

Magpie performs multiple fitness assessments of the original software (default: three) to establish a baseline for comparison.
The final fitness from this warmup phase (by default, the last value) is used as the reference during the optimisation process.
This repeated warmup helps compensate for possible variance in early executions, ensuring fair and stable comparisons.


## Search

Following the warmup, Magpie begins evaluating modified software variants.

```
~~~~ START ~~~~
  ... (lines eluded for clarity) ...
29      TEST_CODE_ERROR       None (--) [2 edit(s)]  
30      TEST_CODE_ERROR       None (--) [2 edit(s)]  
31      TEST_CODE_ERROR       None (--) [2 edit(s)]  
32      TEST_CODE_ERROR       None (--) [2 edit(s)]  
33      SUCCESS              *0.0060 (7.84%) [2 edit(s)]  
34      COMPILE_CODE_ERROR    None (--) [3 edit(s)]  
35      SUCCESS               0.0094 (12.29%) [1 edit(s)] [cached] 
36      SUCCESS               0.0821 (107.32%) [1 edit(s)]  
37      TEST_CODE_ERROR       None (--) [3 edit(s)]  
38      SUCCESS              +0.0060 (7.84%) [3 edit(s)] [cached] 
  ... (lines eluded for clarity) ...
97      SUCCESS              +0.0060 (7.84%) [3 edit(s)] [cached] 
98      TEST_CODE_ERROR       None (--) [2 edit(s)]  
99      SUCCESS              +0.0060 (7.84%) [4 edit(s)] [cached] 
100     COMPILE_CODE_ERROR    None (--) [5 edit(s)]  
~~~~ END ~~~~
```

Each output line includes:
- an evaluation id,
- the outcome status,
- the resulting fitness value, and
- optional comments, such as the number of edits in the patch or whether the fitness was already cached internally.

Magpie reports various statuses to indicate the outcome of each evaluation.
All non-success statuses include the name of the pipeline step where the error occurred.


- **CLI_ERROR**: Magpie failed to run the given command (e.g., missing executable)
- **CODE_ERROR**: the execution yielded a nonzero exit code (e.g., crash, assertion fail)
- **TIMEOUT**: the command exceeded its allowed execution time
- **LENGTHOUT**: the command exceeded its allowed output length
- **PARSE_ERROR**:an output was produced but Magpie failed to parse a fitness value
- **SUCCESS**: the variant executed successfully a produced a valid fitness value

Fitness is shown both as an absolute number and as a percentage relative to the reference fitness.
In this example, lower values indicate better performance (i.e., faster execution), so that values below 100% indicates faster variants, whilst values over 100% indicates slower variants.
Magpie include two special markers:
- an asterisk (`*`) marks a new best fitness values,
- a plus sign (`+`) marks a repeated best value (equal to the current best).


## Final Report

At the end of the search Magpie reports the reason it stopped.
Reasons might include:
- reaching a maximum number of steps (as in this example),
- reaching the total time budget,
- achieving a target fitness value, or
- a manual interruption (e.g., pressing `Ctrl+C`).

It will then summarise the search results and, it an improvement was found, displays the patch and its associated diff.
Note that a much more detailed log can be found in the `_magpie_logs` folder.
For convenience, if an improving patch is found, both a patch and a diff file will also be available.

```
==== REPORT ====
Termination: step budget
Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-cpp_20250417_1744907898.log
Patch file: _magpie_logs/triangle-cpp_20250417_1744907898.patch
Diff file: _magpie_logs/triangle-cpp_20250417_1744907898.diff
Reference fitness: 0.0765
Best fitness: 0.0060

==== BEST PATCH ====
XmlNodeDeletion<stmt>(('triangle.cpp.xml', 'stmt', 1)) | XmlNodeDeletion<stmt>(('triangle.cpp.xml', 'stmt', 4))

==== DIFF ====
--- before: triangle.cpp
+++ after: triangle.cpp
@@ -2,7 +2,7 @@
 
 void delay() {
   const struct timespec ms = {0, (long int) (0.001*1e9)}; //tv_sec=0, tv_nsec (0.001 seconds)
-  nanosleep(&ms,NULL); /*ignores possible errors*/
+   /*ignores possible errors*/
 }
 
 int classify_triangle(double a, double b, double c) {
@@ -11,11 +11,7 @@
   delay();
 
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
