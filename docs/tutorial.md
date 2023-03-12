# Setup

First, download and extract Minisat 2.2.0 (as the real-world target software)
For consistency we extract it here in `example/code`, beside the provided example toy software.

    wget "http://minisat.se/downloads/minisat-2.2.0.tar.gz"
    tar xzf minisat-2.2.0.tar.gz -C examples/code
    rm minisat-2.2.0.tar.gz

Then setup the MiniSAT directory with files used by Magpie.

    patch -d examples/code -p 1 < examples/code/minisat_setup/minisat.patch
    cp examples/code/minisat_setup/data examples/code/minisat
    cp examples/code/minisat_setup/*.sh examples/code/minisat
    cp examples/code/minisat_setup/Solver.cc.xml examples/code/minisat/core
    cp examples/code/minisat_setup/minisat*.params examples/code/minisat

In particular:

- `minisat.patch` is applied to add comment support to MiniSAT's Dimacs parser
- `data` contains 20 instances from [SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
- `compile.sh` simply runs the MiniSAT-provided makefile
- `test.sh` checks MiniSAT's output on 5 SAT and 5 UNSAT instances
- `run.sh` runs MiniSAT on all 20 instances
- `run2.sh` handle the two artificial parameters introduced in `minisat_advanced.params`
- `Solver.cc.xml` contains the AST of the MiniSAT's `core/Solver.cc` file as provided by [SrcML](https://www.srcml.org/).
- `minisat_simplified.params` defines MiniSAT's configuration space
- `minisat_advanced.params` use two additional parameters to improve the configuration space definition


# Scenario Files

We provide five scenarios, all based on the same model (`examples/scenario/minisat_runtime_xml.txt`):

    [magpie]
    default_timeout = 30
    default_lengthout = 1e6

    [software]
    path = examples/code/minisat
    target_files =
        core/Solver.cc.xml
    fitness = time

    compile_cmd = ./compile.sh
    test_cmd = ./test.sh
    run_cmd = ./run.sh

    [search]
    max_steps = 100
    possible_edits =
        StmtReplacement
        StmtInsertion
        StmtDeletion

See [`config.md`](./config.md) for a comprehensive list of possible properties and their default values.

First, the `[magpie]` section provides default limits on execution time (30 seconds) and output length (1e6 bytes, i.e., 1 Mo), which is enough for the different scripts (`compile.sh`, `test.sh`, `run.sh`) for the different scripts to complete without issue.

Then the `[software]` section specifies where the original software is located, which file(s) will be mutated, the three scripts that serve for fitness evaluation, as well as the type of fitness to be calculated.

Finally, the `[search]` section describes the parameters used during search, here the maximum number of steps, and the list of possible edits.


We provide six scenarios for MiniSAT, that cover two fitness functions (execution time, and source code size) as well as three representations (AST through XML, lines of code, and configuration files).

- `examples/scenario/minisat_runtime_xml1.txt`
- `examples/scenario/minisat_runtime_xml2.txt`
- `examples/scenario/minisat_runtime_line.txt`
- `examples/scenario/minisat_runtime_config1.txt`
- `examples/scenario/minisat_runtime_config2.txt`
- `examples/scenario/minisat_bloat.txt`


# Experiments

## Search

Magpie provides two types of search algorithms: local search and genetic programming.

Example:

    python3 -m bin.local_search --scenario examples/scenario/minisat_runtime_xml1.txt
<!-- -->
    python3 -m bin.genetic_programming --scenario examples/scenario/minisat_runtime_line.txt

If a specific search algorithm is provided, either in the scenario file or directly (at higher precedence) through the command line (at higher precedence), it will be used in place of the default one.

    python3 -m bin.local_search --scenario examples/scenario/minisat_runtime_xml1.txt --algo rand
<!-- -->
    python3 -m bin.genetic_programming --scenario examples/scenario/minisat_runtime_xml1.txt --algo gp_uinter


## Simplification

It is probable that search resulted in a possible patch.
However, depending on the search trajectory, it is possible that the patch is incorrect or bloated.

As an example, we will first assume having generated the following patch using the `minisat_runtime_xml1.txt` scenario:

    StmtDeletion(('core/Solver.cc.xml', 'stmt', 299)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 256)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 187)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 254)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 345)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 49)) | StmtReplacement(('core/Solver.cc.xml', 'stmt', 134), ('core/Solver.cc.xml', 'stmt', 20)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 387)) | StmtReplacement(('core/Solver.cc.xml', 'stmt', 258), ('core/Solver.cc.xml', 'stmt', 17)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 67)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 395)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 24)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 61)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 59)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 343))

First, we can double-check the associated diff with the `show_patch` entry point.

    python3 -m bin.show_patch --scenario examples/scenario/minisat_runtime_config2.txt --patch "StmtDeletion(('core/Solver.cc.xml', 'stmt', 299)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 256)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 187)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 254)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 345)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 49)) | StmtReplacement(('core/Solver.cc.xml', 'stmt', 134), ('core/Solver.cc.xml', 'stmt', 20)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 387)) | StmtReplacement(('core/Solver.cc.xml', 'stmt', 258), ('core/Solver.cc.xml', 'stmt', 17)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 67)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 395)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 24)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 61)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 59)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 343))"

Note that all entry points that require a patch (e.g., `show_patch`, `revalidate_patch`, `minify_patch`, `ablation_analysis`) also accept the path of a file countaining said patch.
Patches generated by previous successful Magpie executions may be found alongside log files in the `_magpie_logs` folder.

    python3 -m bin.show_patch --scenario examples/scenario/minisat_runtime_config2.txt --patch path/to/my/patch

The `show_patch` entry point simply applies the patch but does not calculate its fitness.
Instead, the `revalidate_patch` can be used to that purpose.

In our case, the patch is quite long (as is the diff), which can make it unnecessarily hard to understand and trust.
Unneeded edits may also make it more fragile.
To simplify the patch, one may use the `minify_patch` entry point.

    python3 -m bin.minify_patch --scenario examples/scenario/minisat_runtime_xml1.txt --patch "StmtDeletion(('core/Solver.cc.xml', 'stmt', 299)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 256)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 187)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 254)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 345)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 49)) | StmtReplacement(('core/Solver.cc.xml', 'stmt', 134), ('core/Solver.cc.xml', 'stmt', 20)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 387)) | StmtReplacement(('core/Solver.cc.xml', 'stmt', 258), ('core/Solver.cc.xml', 'stmt', 17)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 67)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 395)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 24)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 61)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 59)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 343))"

However, depending on the possible noise related to measuring running time, it is possible for the patch to still be bloated.
In that case, it is definitely possible to try re-minifying it or simply to rerun the minification process starting from the original patch.

Finally, the `ablation_analysis` entry point may be useful to compare the individual contribution of each edit in the patch.

    python3 -m bin.ablation_analysis --scenario examples/scenario/minisat_runtime_xml1.txt --patch "StmtDeletion(('core/Solver.cc.xml', 'stmt', 299)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 256)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 187)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 254)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 345)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 49)) | StmtReplacement(('core/Solver.cc.xml', 'stmt', 134), ('core/Solver.cc.xml', 'stmt', 20)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 387)) | StmtReplacement(('core/Solver.cc.xml', 'stmt', 258), ('core/Solver.cc.xml', 'stmt', 17)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 67)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 395)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 24)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 61)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 59)) | StmtDeletion(('core/Solver.cc.xml', 'stmt', 343))"

The analysis yields the following output:

    ==== ANALYSIS ====
    ~       SUCCESS               15.7065 (63.75%) [14 edit(s)] 
    ~       SUCCESS               15.6406 (63.48%) [13 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 387))
    ~       SUCCESS               16.2835 (66.09%) [12 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 299))
    ~       SUCCESS               15.8741 (64.43%) [11 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 24))
    ~       SUCCESS               15.8965 (64.52%) [10 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 343))
    ~       SUCCESS               15.7445 (63.9%) [9 edit(s)] removing StmtReplacement(('core/Solver.cc.xml', 'stmt', 134), ('core/Solver.cc.xml', 'stmt', 20))
    ~       SUCCESS               15.6441 (63.49%) [8 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 254))
    ~       SUCCESS               15.8172 (64.2%) [7 edit(s)] removing StmtReplacement(('core/Solver.cc.xml', 'stmt', 258), ('core/Solver.cc.xml', 'stmt', 17))
    ~       SUCCESS               15.4485 (62.7%) [6 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 187))
    ~       SUCCESS               16.1452 (65.53%) [5 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 256))
    ~       SUCCESS               16.1127 (65.4%) [4 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 59))
    ~       SUCCESS               15.6165 (63.38%) [3 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 67))
    ~       SUCCESS               16.1816 (65.67%) [2 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 49))
    ~       SUCCESS               15.7627 (63.97%) [1 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 395))
    ~       SUCCESS               24.639 (100.0%) [0 edit(s)] removing StmtDeletion(('core/Solver.cc.xml', 'stmt', 345))

We can see that the running time improvement is almost exclusively due to a single edit: `StmtDeletion(('core/Solver.cc.xml', 'stmt', 395))`.
The other edits have no significant impact on the overall patch fitness, mostly indistinguishable from noise.
The `show_patch` entry point can pinpoint the specific change in diff form:

    --- before: core/Solver.cc
    +++ after: core/Solver.cc
    @@ -959,16 +959,7 @@
             }/*auto*/

         for (int i = 0; i < clauses.size(); i++)
    -        /*auto*/{if (!satisfied(ca[clauses[i]])){
    -            Clause& c = ca[clauses[i]];
    -            for (int j = 0; j < c.size(); j++)
    -                /*auto*/{if (value(c[j]) != l_False)
    -                    /*auto*/{mapVar(var(c[j]), map, max);
    -
    -                    }/*auto*/
    -
    -                }/*auto*/
    -        }
    +        /*auto*/{

             }/*auto*/


---

Similarly, let's assume to have generated the following patch using the `minisat_runtime_config2.txt` scenario:

    ParamSetting(('minisat_advanced.params', 'luby'), 'False') | ParamSetting(('minisat_advanced.params', 'rfirst'), 210) | ParamSetting(('minisat_advanced.params', 'verb'), '0')

Three parameters are changed:

    --- before: minisat_advanced.params
    +++ after: minisat_advanced.params
    @@ -1,4 +1,4 @@
    -luby := 'True'
    +luby := 'False'
     rnd-init := 'False'
     gc-frac := 0.2
     rinc := 2.0
    @@ -8,9 +8,9 @@
     rnd-seed := 91648253
     phase-saving := 2
     ccmin-mode := 2
    -rfirst := 100
    +rfirst := 210
     pre := 'True'
    -verb := '1'
    +verb := '0'
     rcheck := 'False'
     asymm := 'False'
     elim := 'True'

Note that for parameter setting edits Magpie does not actually produces a diff of the configuration file, as those are not natively used by the target software, but rather focuses on showing the differences to the default configuration.

Let us perform an ablation analysis:

    python3 -m bin.ablation_analysis --scenario examples/scenario/minisat_runtime_config2.txt --patch "ParamSetting(('minisat_advanced.params', 'luby'), 'False') | ParamSetting(('minisat_advanced.params', 'rfirst'), 210) | ParamSetting(('minisat_advanced.params', 'verb'), '0')"

Giving the following output:

    ==== ANALYSIS ====
    ~       SUCCESS               4.5381 (17.6%) [3 edit(s)] 
    ~       SUCCESS               4.5479 (17.63%) [2 edit(s)] removing ParamSetting(('minisat_advanced.params', 'rfirst'), 210)
    ~       SUCCESS               5.524 (21.42%) [1 edit(s)] removing ParamSetting(('minisat_advanced.params', 'verb'), '0')
    ~       SUCCESS               25.7901 (100.0%) [0 edit(s)] removing ParamSetting(('minisat_advanced.params', 'luby'), 'False')

It show that the most impactful change is by far the setting of the `luby` parameter to `False`, speeding up Minisat from 25.8 seconds to only 5.5 seconds.
Disabling `verb` ("verbose") yields a further 1 second improvement, and the setting of the `rfist` parameter is not significant and may be safely ignored.
