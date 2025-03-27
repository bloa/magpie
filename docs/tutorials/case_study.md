# Case Study: MiniSAT

This tutorial walks through applying Magpie to a real-world software project: MiniSAT, a popular SAT solver.
It covers:
1. setting up the environment, both manually and automatically;
2. exploring different levels of granularity when searching for patches:
  - line-level modifications,
  - AST-based transformations,
  - tuning runtime parameters for performance;
3. using dynamic benchmarks.

Each section provides step-by-step instructions, example command lines, and expected outcomes, guiding you through using Magpie to analyse and optimise MiniSAT.
By the end, you'll have a clear understanding of how to apply Magpie to your own software projects.


## Manual Setup

There are pre-configured files available under examples/magpie, but for now, let's ignore them and go through the entire setup process step by step.
This will help you understand how to prepare a new software project for Magpie from scratch.

To use Magpie, you will need to provide at least a directory containing the source code of your software and descriptions of how to compile it (if required), test it against a suite of test cases (if needed), and run it on a benchmark (for performance optimisation).
All of these information is bundled into a **scenario file**, which Magpie uses to manage its search process.

### Source code

We first download MiniSAT and place it in a dedicated directory.
For consistency with other examples, we'll use `examples/tutorial_minisat`, but you can choose any location.
Just keep in mind that Magpie makes a copy of this directory when compiling and evaluating software variants, so ensures it's small and clean to avoid unnecessary overhead.

The following commands should set up our source directory:
```
wget "http://minisat.se/downloads/minisat-2.2.0.tar.gz"
tar xzf minisat-2.2.0.tar.gz -C examples/tutorial_minisat
rm minisat-2.2.0.tar.gz
```

### Compilation

MiniSAT's build process is straightforward, but you may need to adjust compiler flags depending on your system.
To ensure reproducibility and ease of use, encapsulate the compilation command in a script:

**examples/tutorial_minisat/compile.sh**
```bash
#!/bin/sh
MROOT=.. CFLAGS=-fpermissive make -C simp
```

Make this script executable so that Magpie can run it automatically:

    chmod +x examples/tutorial_minisat/compile.sh

Magpie will sync the evaluation directory before every run, ensuring a clean starting state for every software variant.
This eliminates the need for cleanup inside the compilation process.
On the contrary, if your build process supports incremental compilation, Magpie will be able to take advantage of it to speed up evaluations.


### Test suite

MiniSAT does not come with a built-in test suite.
This will cause issues as we modify its source code as it may break or introduce bugs.
To ensure that each software variant still functions correctly, we'll write a script that will runs MiniSAT on a select subset of known easy instances to verify its output.
We'll use 6 SAT instances (for which MiniSAT should have a return code of `10`) and 6 UNSAT instances (on which it should have a return code of `20`).
These instances are provided in `examples/minisat/data`, so we simply copy them over.

    cp -r examples/minisat/data examples/tutorial_minisat

Note that since we place them _inside_ the source directory, they will be duplicated inside Magpie's evaluation directory.
This may result in an initial copy overhead, which might be problematic with very large datasets, however since Magpie sync the evaluation directory before any new software variant rather than recreating from scratch, the long-term cost is minimal.
The alternative would be to leave them _outside_ the source directory, which would require referring to them using absolute paths, making the setup less portable.

Unfortunately, due to the format of these instances---which include a final non-standard comment section starting with "%"---a very short patch needs to be applied on MiniSAT source code (`core/Dimacs.h`):

```
--- core/Dimacs.h       2010-07-10 17:07:36.000000000 +0100
+++ core/Dimacs.h       2019-12-12 16:34:08.524833459 +0000
@@ -65,6 +65,8 @@
             }
         } else if (*in == 'c' || *in == 'p')
             skipLine(in);
+        else if (*in == '%')
+            break;
         else{
             cnt++;
             readClause(in, S, lits);
```

**examples/tutorial_minisat/test.sh**
```bash
#!/bin/sh

ARGV=$@

my_test() {
    FILENAME=$1
    EXPECTED=$2
    ./simp/minisat $FILENAME $ARGV > /dev/null
    RETURN=$?
    if [ $RETURN -ne $((EXPECTED)) ]; then
	echo "FAILED ON FILE:" $FILENAME
	echo "GOT:" $RETURN
	echo "EXPECTED:" $EXPECTED
	exit -1
    fi
}
 
my_test data/uf50-01.cnf 10
my_test data/uf50-02.cnf 10
my_test data/uf100-01.cnf 10
my_test data/uf100-02.cnf 10
my_test data/uf150-01.cnf 10
my_test data/uf150-02.cnf 10

my_test data/uuf50-01.cnf 20
my_test data/uuf50-02.cnf 20
my_test data/uuf100-01.cnf 20
my_test data/uuf100-02.cnf 20
my_test data/uuf150-01.cnf 20
my_test data/uuf150-02.cnf 20
```

Again, make this script executable so that Magpie can run it automatically:

    chmod +x examples/tutorial_minisat/test.sh


### Benchmark

Finally, let's write a third script, this time using a (fixed) much larger set of instances so we can evaluate the performance of our software variants.

**examples/tutorial_minisat/run_fixed.sh**
```bash
#!/bin/sh

./simp/minisat data/uf50-01.cnf $@
./simp/minisat data/uf50-02.cnf $@
./simp/minisat data/uf100-01.cnf $@
./simp/minisat data/uf100-02.cnf $@
./simp/minisat data/uf150-01.cnf $@
./simp/minisat data/uf150-02.cnf $@
./simp/minisat data/uf200-01.cnf $@
./simp/minisat data/uf200-02.cnf $@
./simp/minisat data/uf250-01.cnf $@
./simp/minisat data/uf250-02.cnf $@

./simp/minisat data/uuf50-01.cnf $@
./simp/minisat data/uuf50-02.cnf $@
./simp/minisat data/uuf100-01.cnf $@
./simp/minisat data/uuf100-02.cnf $@
./simp/minisat data/uuf150-01.cnf $@
./simp/minisat data/uuf150-02.cnf $@
./simp/minisat data/uuf200-01.cnf $@
./simp/minisat data/uuf200-02.cnf $@
./simp/minisat data/uuf250-01.cnf $@
./simp/minisat data/uuf250-02.cnf $@

exit 0
```

Again, make this script executable so that Magpie can run it automatically:

    chmod +x examples/tutorial_minisat/run_fixed.sh

Note that the `$@` at the end of each call to MiniSAT is used to forward command line parameters from the overall `run_fixed.sh` script.
This will be useful when operating at the command line granularity (Scenario 3).


## Scenario 1: Evolving Lines of Code

This scenario sets up a basic configuration to apply line-level edits to MiniSAT.

```
[magpie]
default_timeout = 30
default_lengthout = 1e6

[software]
path = examples/minisat_tutorial
target_files =
    core/Solver.cc
fitness = time

setup_cmd = bash compile.sh
compile_cmd = bash compile.sh
test_cmd = bash test.sh
run_cmd = bash run_fixed.sh

[search]
max_steps = 100
possible_edits =
    LineReplacement
    LineInsertion
    LineDeletion
```

We start by updating Magpie's defaults values runtime constraints: each execution is capped to 30 seconds and one million characters of combined STDOUT+STDERR output.
These limits ensure that the worst MiniSAT software variants won't needlessly waste compute or flood Magpie's cache.

Next, we define the core parameters for the software under study.
The source code resides in `examples/minisat_tutorial`, supposing that you are working step by step following this tutorial.
We restrict patch generation to the file `core/Solver.cc`, which contains much of MiniSAT's core logic.
If needed, you could target additional files by listing them explicitly or using wildcards:

```
target_files =
    core/Solver.cc
    core/*.cc
```

For this tutorial, we use `time` as the fitness measure, since it doesn't add any requirement.
You may however want to use a more precise time-based fitness (e.g., `gnutime<wall clock>` or `perf<time elapsed>`) or to switch to CPU instructions (`perf<instructions/u>`).
Note that it will require you to update the `run_cmd` command, e.g., to `/usr/bin/time -v bash run_fixed.sh` or `perf stat bash run_fixed.sh`, and, of course, having a GNU-compatible `time` or `perf` on your machine.

Finally, we specify the commands that Magpie uses to interact with the software: `setup_cmd` (executed once before the search), `compile_cmd`, `test_cmd`, and `run_cmd` to use the previously defined scripts.
In the `examples/minisat/_magpie` version of this scenario, you'll also find an `init_cmd` to automatically download, cache, and prepare MiniSAT's source code.

The last section keeps the search short by limiting it to 100 steps.
It enables three types of possible line-level edits: insertions, deletions, and replacements.


## Scenario 2: Evolving ASTs

In the previous scenario, Magpie worked at line granularity because the target file (`core/Solver.cc`) wasn't linked to a structured model.
In contrast, here, we switch to a tree-based (AST) granularity by targeting the equivalent XML representation of the source file.

```
[magpie]
default_timeout = 30
default_lengthout = 1e6

[software]
path = examples/minisat_tutorial
target_files = core/Solver.cc.xml
fitness = time

setup_cmd = bash compile.sh
compile_cmd = bash compile.sh
test_cmd = bash test.sh
run_cmd = bash run_fixed.sh

[search]
max_steps = 100
possible_edits =
    XmlNodeDeletion<stmt>
    XmlNodeReplacement<stmt>
    XmlNodeInsertion<stmt,block>
```

By targeting `Solver.cc.xml`, Magpie automatically applies an AST model (SrcmlModel) rather that the default line model.
By default, all files ending with a .xml extension are treated as ASTs and use the "[srcml]" section, all files ending with a ".params" extension are treated as configuration files and use the "[paramconfig]" section, whilst all others are simply handled as lists of lines of text.
You can explicitly specify how files are controlled using `[software] model_rule`, and even assign model-specific configuration using `[software] model_config`.

```
[software]
model_rules =
    *.params : ParamFileConfigModel
    *.xml : SrcmlModel
    * : LineModel
model_config =
    *.params : [paramconfig]
    *.xml : [srcml]
```

Note that the default XML-based model, `SrcmlModel`, will strip the .xml extension and produce a modified variant of `Solver.cc`, _not_ `Solver.cc.xml`.

To generate ASTs from C/C++/Java/C# source code, you can use [SrcML](https://www.srcml.org/), which outputs XML-structured code.
Magpie also includes a simple `python_to_xml` utility that converts Python files into XML using Python's built-in parsing.
For convenience, a pre-generated Solver.cc.xml is already available in `examples/minisat/_magpie`.

Finally, because we've changed model, we also must update the types of edits that Magpie can apply.
Note that `<stmt>` isn't a node type that appear in the `Solver.cc.xml` file, nor is one generated by SrcML.
This is because Magpie will by default internally rename and group AST nodes to follow the most common GI experimentation setup, based on the following default config:

```
[srcml]
rename =
    stmt: break continue decl_stmt do expr_stmt for goto if return switch while
    number: literal_number
focus = block stmt operator_comp operator_arith number
internodes = block
process_pseudo_blocks = True
process_literals = True
process_operators = True
```

In particular:
- many nodes including `<break>`, `<continue>`, `<decl_stmt>` are renamed as simply `<stmt>`;
- `<literal_number>` is simplified to `<number>`, following `process_literals`;
- some operators are renamed into `<operator_comp>` and `<operator_arith>`, following `process_operators`;
- all tags except `<block>`, `<stmt>`, `<operator_comp>`, `<operator_arith>`, and `<number>` are deleted;
- one-line blocks without braces are made explicit to avoid syntax errors when editing; and finally
- `<block>` nodes are internally processed to enable later node insertion.


## Scenario 3: Evolving Runtime Parameters

In the third scenario we explore how Magpie can optimise the runtime configuration of MiniSAT.
The setup is nearly identical to Scenario 2, with two key changes:
- the target file is now a .params file that describes the configuration space
- the edit type is now `ParamSetting`, allowing changes in that .params file.

```
[magpie]
default_timeout = 30
default_lengthout = 1e6

[software]
path = examples/minisat_tutorial
target_files = minisat_simplified.params
fitness = time

setup_cmd = bash compile.sh
compile_cmd =
test_cmd = bash test.sh
run_cmd = bash run_fixed.sh

[search]
max_steps = 1000
max_time = 60
possible_edits = ParamSetting
```

The parameter file `minisat_simplified.params` is provided in `examples/minisat`.
It defines both the formatting of the command line interface and the details regarding all tunable parameters.
For clarity, a snippet of this file is show below, showing the header and few core parameters.

```
CLI_PREFIX = "-"
CLI_GLUE = "="
CLI_BOOLEAN = "prefix"

# core
luby      {True, False}[True]
rnd-init  {True, False}[False]
gc-frac   e(0, 65535)[0.2]
rinc      e(1, 65535)[2]
var-decay (0, 1)[0.95]

phase-saving [0, 2][2]
ccmin-mode   [0, 2][2]
rfirst       g[1, 65535][100]
```

Each parameter includes:
- a name (e.g., `luby`);
- a range or set of values (e.g., `(0, 1)` or `{True, False}`); and
- a default value (inside square brackets).

At evaluation time, all parameters are gathered and formatted according to the chosen specification.
Here, instead of running `bash run_fixed.sh` as specified as `run_cmd`, Magpie would for example run `bash run_fixed.sh -luby -no-rdn-init -gcfrac=0.2 -rinc=2`.

Magpie supports:
- categorical parameters (e.g., `{foo, bar, baz}`, with optional support for specific value such as "True", "False", and "None");
- continuous parameters with uniform (e.g., `(0, 1)`) and exponential (e.g., `e(0, 1)`) sampling;
- integer parameters with uniform (e.g., `[0, 10]`) and geometric (e.g., `g[0, 10]`) sampling;
- hidden, conditional, and forbidden parameters (not shown here).


## Scenario 4: Dynamic Benchmarks

In this final scenario, we show how Magpie can easily adapt to cases in which benchmarks are frequently updated, for example when the full set of available instances is too large to evaluate every time or if you're interested in measuring generalisation over a diverse set of inputs.

Recall that we wrote `examples/tutorial_minisat/run_fixed.sh` to explicitly run MiniSAT on a fixed list of benchmark instance.
This works well for small sets, but it can quickly become cumbersome for quick testing or larger datasets.
Instead, let's simplify the evaluation script to only run MiniSAT once on a single input instance.

**examples/tutorial_minisat/run_single.sh**
```bash
#!/bin/sh

./simp/minisat $@

exit 0
```

We can then instruct Magpie to handle the benchmark repetition and sampling strategy internally:

```
[magpie]
default_timeout = 30
default_lengthout = 1e6

[software]
path = examples/minisat_tutorial
target_files =
    core/Solver.cc
fitness = time

init_cmd = bash init.sh
setup_cmd = bash compile.sh
compile_cmd = bash compile.sh
test_cmd = bash test.sh
run_cmd = bash run_single.sh {INST}

[search]
max_steps = 100
batch_instances =
    file:data/inst_sat.txt
    ___
    file:data/inst_unsat.txt
batch_sample_size = 4
possible_edits =
    LineReplacement
    LineInsertion
    LineDeletion
```

Key changes:
- `[software] run_cmd` uses the new script and now includes "{INST}" as a placeholder that Magpie will replace with the input file path;
- `[search] batch_instances` lists two files corresponding to SAT and UNSAT instances, separated with `___`;
- `[search] batch_sample_size` specify that four instances should be sampled (at the beginning of the search).


If you want more explicit control over which instances are sampled, you can also list them directly:

```
[search]
batch_instances =
    data/uf50-01.cnf
    data/uf50-02.cnf
    data/uuf50-01.cnf
    data/uuf50-02.cnf
    ___
    data/uf100-01.cnf
    data/uf100-02.cnf
    data/uuf100-01.cnf
    data/uuf100-02.cnf
    ___
    data/uf150-01.cnf
    data/uf150-02.cnf
    data/uuf150-01.cnf
    data/uuf150-02.cnf
    ___
    data/uf200-01.cnf
    data/uf200-02.cnf
    data/uuf200-01.cnf
    data/uuf200-02.cnf
    ___
    data/uf250-01.cnf
    data/uf250-02.cnf
    data/uuf250-01.cnf
    data/uuf250-02.cnf
batch_sample_size = 5
```

This example specifies five bins of problem sizes, sampling one instance per bin uniformly at random (with no guarantee on the instances satisfiability).
