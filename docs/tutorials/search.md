# Searching for improved variants

In this tutorial we are concerned by running Magpie to find improved variant of a given software.
We will consider two use cases, a first one in which we want to improve execution time, and a second in which we aim to fix a semantic bug.

## **examples/triangle-c**

Both use cases will use the same target software: **examples/triangle-c**.
This example involves five core files.

- **triangle.h**: defines the software interface
- **triangle.c**: contains the software implementation
- **standalone.c**: provides a generic entry point
- **test_triangle.c**: contains the software test suite
- **makefile**: compiles everything


## Use case 1: improving execution time

### **examples/triangle-c**

We consider one more core file: **run_triangle.c**.
It contains a "real world" use case of the software, which we will use as a payload for which we want to reduce execution time.


### Magpie scenario

We consider **examples/triangle-c/_magpie/scenario_slow.txt**.

    [software]
    path = examples/triangle-c
    target_files =
        triangle.c.xml
    fitness = time

    init_cmd = bash init_slow.sh
    compile_cmd = make test_triangle run_triangle
    test_cmd = ./test_triangle
    run_cmd = ./run_triangle
    run_timeout = 1

    [search]
    max_steps = 100
    max_time = 60
    possible_edits =
        SrcmlStmtReplacement
        SrcmlStmtInsertion
        SrcmlStmtDeletion

We use the **examples/triangle-c** example, focusing on a single file: **triangle.c.xml**, optimising **time**.
We define four command lines:

- **init_cmd**: introduces a fault in our software (making it slower, so we can make it faster again) and provides the **triangle.c.xml** file that will be evolved.
- **compile_cmd**: compiles the test suite and the payload.
- **test_cmd**: runs the test suite
- **run_cmd**: runs the payload

As for the search, for the purpose of this tutorial we limit it to _either_ **100 steps** or **60 seconds**, whatever happens first.

In the following, by "initial software" we mean the software such as it is after the "init" step, i.e., including the seeded performance bug.


### Magpie run

Let's run a local search.
We do that by simply running the (local) magpie module using `python3 magpie`, using the `local_search` entry point, and specifying the desired scenario file.

    python3 magpie local_search --scenario examples/triangle-c/_magpie/scenario_slow.txt

Magpie starts with evaluating the initial software three times, using the latest measurement as baseline (**0.0808 seconds**).

    ==== WARMUP ====
    WARM    SUCCESS               0.0804                  
    WARM    SUCCESS               0.0762                  
    WARM    SUCCESS               0.0808                  
    INITIAL SUCCESS               0.0808                  

The fault should be easy enough to be fix in almost every run.
You should be seeing lines such that:

    22      SUCCESS               0.0788 (97.52%) [1 edit(s)] 
    23      SUCCESS              *0.0049 (6.06%) [1 edit(s)] 
    24      TEST_CODE_ERROR       None  [2 edit(s)] 

In this case, the 22th software variant applied a single modification to the original software and ran the payload in **0.0788 seconds**, very slightly faster (**97.52%** of the initial fitness of **0.0808 seconds**).

The 23th software variant ran in **0.0049** seconds, (much faster: **6.06%** or the initial fitness).
The **\*** asterisk indicates that this is a new best fitness value.

The 24th software variant failed to complete the test suite.


### Final report

If Magpie found a fix, it will then produce a report similar to

    ==== REPORT ====
    Termination: time budget
    Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-c_1709750917.log
    Patch file: _magpie_logs/triangle-c_1709750917.patch
    Diff file: _magpie_logs/triangle-c_1709750917.diff
    Initial fitness: 0.0808
    Best fitness: 0.0049
    Best patch: SrcmlStmtDeletion(('triangle.c.xml', 'stmt', 1))
    Diff:
    --- before: triangle.c
    +++ after: triangle.c
    @@ -2,7 +2,7 @@

     void delay() {
       const struct timespec ms = {0, (long int) (0.001*1e9)}; //tv_sec=0, tv_nsec (0.001 seconds)
    -  nanosleep(&ms,NULL); /*ignores possible errors*/
    +   /*ignores possible errors*/
     }

     int classify_triangle(double a, double b, double c) {

In my case, Magpie stopped after 60 seconds.
It successfully found a patch, lowering the initial fitness of **0.0808 seconds** to **0.0049 seconds**.
The patch contain a single edit, **SrcmlStmtDeletion(('triangle.c.xml', 'stmt', 1))**, which deletes one statement.
Looking at the diff, the deleted statement is **nanosleep(&ms,NULL);**.

The paths to three files are provided:
- **_magpie_logs/{software}_{timestamp}.log**: provides the complete output
- **_magpie_logs/{software}_{timestamp}.patch**: contains the best patch in Magpie's internal representation
- **_magpie_logs/{software}_{timestamp}.diff**: contains the best patch in diff representation

### Obtaining a patched variant

We just saw a possible fix:

    SrcmlStmtDeletion(('triangle.c.xml', 'stmt', 1))

It was found by Magpie, and its diff was also recorded, but the actual software variant was not automatically preserved.

To obtained the patched variant on disk, we use the **show_patch** entry point together with the **--keep** option.

    python3 magpie show_patch --scenario examples/triangle-c/_magpie/scenario_bug.txt --patch "SrcmlStmtDeletion(('triangle.c.xml', 'stmt', 1))" --keep

This time, in addition of the _normal_ output of **show_patch** (recomputing the diff), Magpie will write the desired variant on disk, at the path indicated at the end of its output:

    ==== PATH ====
    /home/aymeric/git/magpie/_magpie_work/triangle-c_1709828671


## Use case 2: automated bug fixing

### Magpie scenario

This time we consider **examples/triangle-c/_magpie/scenario_bug.txt**.

    [software]
    path = examples/triangle-c
    target_files =
        triangle.c.xml
    fitness = repair

    init_cmd = bash init_bug.sh
    compile_cmd = make test_triangle
    test_cmd = ./test_triangle

    [search]
    target_fitness = 0
    max_steps = 100
    possible_edits =
        SrcmlStmtReplacement
        SrcmlStmtInsertion
        SrcmlStmtDeletion

As opposed to the previous **scenario_slow.txt** scenario, the fitness is now **repair**, and we don't need a command to run the software (nor do we need to compile the **run_software** entry point).

Additionally, **target_fitness** is set to **0** to stop immediately after finding a bug-free software variant (which is very much harder than in the first example).


## Using the _repair_ fitness function

Our example test suite (**test_triangle.c**) outputs the total number of tests and the number of failed tests.

    printf("Tests run: %d\n", passed+failed);
    printf("Failures: %d\n", failed);

Magpie _absolutely requires_ both these figures to compute a software fitness value, and does so by computing their ratio as a percentage.
For example, the initial software of **scenario_slow.txt** reports a fitness value of **33.33**, meaning that one third of the test cases failed.
Without checking that the total number is non-zero, Magpie wouldn't be able to distinguish between a software with no failed tests, and one that would make the test runner crash gracefully.


## Magpie run

This time, let's run a genetic programming search.

    python3 magpie genetic_programming --scenario examples/triangle-c/_magpie/scenario_bug.txt

Unfortunately, this example is much harder than the previous one, and there is little chance for Magpie to find an adequate fix in under 100 steps (for either the local search or the genetic programming approach).
More likely, Magpie found a patch that improved the fitness, without reaching the target of zero failed test.

For example, the following is one such outcome:

    Initial fitness: 33.33
    Best fitness: 19.05
    Best patch: SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 16), ('triangle.c.xml', 'stmt', 6))
    Diff:
    --- before: triangle.c
    +++ after: triangle.c
    @@ -28,7 +28,7 @@
       }/*auto*/
       if(a == b && b == c)/*auto*/{

    -    return ISOSCELES;
    +    tmp = a;
       }/*auto*/ // TODO: fixme
       if(a == b || b == c)/*auto*/{

The number of failed tests dropped to 19.05% from the initial 33%, with one replacement.
The patch is not perfect, but by hinting at one possible root cause it could help a developer produce a correct fix.



### Obtaining a patched variant

Let's consider the following patch:

    SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 16), ('triangle.c.xml', 'stmt', 18)) | SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 18), ('triangle.c.xml', 'stmt', 16))

It consist in two successive replacements, swapping the content of the statement nodes 16 and 18.

We can verify the associated diff:

    python3 magpie show_patch --scenario examples/triangle-c/_magpie/scenario_bug.txt --patch "SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 16), ('triangle.c.xml', 'stmt', 18)) | SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 18), ('triangle.c.xml', 'stmt', 16))"

The **show_patch** utility only serve at... showing the patch.
To compute the fitness of the associated fitness variant, let's use **revalidate_patch** instead.

    python3 magpie revalidate_patch --scenario examples/triangle-c/_magpie/scenario_bug.txt --patch "SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 16), ('triangle.c.xml', 'stmt', 18)) | SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 18), ('triangle.c.xml', 'stmt', 16))"

This time, Magpie actually recompiles and run the software variant, confirming a fitness value of 0, i.e., zero failed test.
Here follows the complete output:

    ==== WARMUP ====
    WARM    SUCCESS               33.33                   
    WARM    SUCCESS               33.33                   
    WARM    SUCCESS               33.33                   
    INITIAL SUCCESS               33.33                   
    ==== START: ValidTest ====
    1       SUCCESS              *0.0 (0.0%) [2 edit(s)]  
    ==== END ====

    ==== REPORT ====
    Termination: validation end
    Log file: /home/aymeric/git/magpie/_magpie_logs/triangle-c_1709927677.log
    Patch file: _magpie_logs/triangle-c_1709927677.patch
    Diff file: _magpie_logs/triangle-c_1709927677.diff
    Initial fitness: 33.33
    Best fitness: 0.0
    Best patch: SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 16), ('triangle.c.xml', 'stmt', 18)) | SrcmlStmtReplacement(('triangle.c.xml', 'stmt', 18), ('triangle.c.xml', 'stmt', 16))
    Diff:
    --- before: triangle.c
    +++ after: triangle.c
    @@ -28,11 +28,11 @@
       }/*auto*/
       if(a == b && b == c)/*auto*/{

    -    return ISOSCELES;
    +    return EQUILATERAL;
       }/*auto*/ // TODO: fixme
       if(a == b || b == c)/*auto*/{

    -    return EQUILATERAL;
    +    return ISOSCELES;
       }/*auto*/ // TODO: fixme
       return SCALENE;
     }

First (**WARMUP**) Magpie runs the initial bugged software, then (**START**) it runs the validation algorithm ValidTest, which simply runs once the provided patch, then it reports its finding, linking to the different output files and showing the diff computed from the patch.
