# Basic Usage

We provide four generic entry points for optimsiation/learning/training.

    bin
    ├── magpie_bloat.py
    ├── magpie_config.py
    ├── magpie_repair.py
    └── magpie_runtime.py

Because they are located in a sub-folder and not at top-level, they require a little bit of Python magic speach (e.g., `python -m bin.magpie_runtime` instead of `python magpie_runtime.py`).
To simplify usage we strongly recommend writting your own customised entry point and running it from top-level.

For the sake of genericity, note that all four scripts only target lines of code mutations and use a basic local search.
To target AST nodes, change the search algorithm, the fitness function, or modify the experimental protocol in general please refer to [ADVANCED.md](/ADVANCED.md).


## Running Time Minimisation

Example:

    python -m bin.magpie_runtime --config examples/scenario/triangle-py_runtime.txt


## Automated Bug Fixing

Example:

    python -m bin.magpie_repair --config examples/scenario/triangle-rb_repair.txt

See also: (with expression and operator mutations)

    python -m examples.magpie_repair_xml_java --config examples/scenario/triangle-java_repair_srcml.txt


## Bloat Minimisation

Example:

    python -m bin.magpie_bloat --config examples/scenario/triangle-py_bloat.txt

See also: (to remove empty lines and comments from the location list)

    python -m examples.magpie_bloat2 --config examples/scenario/triangle-py_bloat.txt


## Algorithm Configuration

See the [real world example](#real-world-example) for instructions on how to setup MiniSAT.

Example:

    python -m bin.magpie_config --config examples/scenario/minisat_config.txt

See also: (for fine-tuned parameter handling)

    python -m examples.magpie_config_minisat --config examples/scenario/minisat_config_advanced.txt


# Validation

We provide three generic entry points for validation/test.

    bin
    ├── ablation_analysis.py
    ├── minify_patch.py
    └── revalidate.py

Note that these script require knowledge of the scenario specifics.
They are written to work out-of-the-box with the other provided entry points, but expect having to modify them to follow your specific experimental setup (e.g., to reflect changes in the fitness function, the types of mutations, etc).
Again, please refer to [ADVANCED.md](/ADVANCED.md) to help modifying entry points.


## Fitness Reassessment

Example: (using the running time minimisation example)

    python -m bin.revalidate --mode runtime --config examples/scenario/triangle-py_runtime.txt --patch "LineReplacement(('triangle.py', 'line', 31), ('triangle.py', 'line', 25)) | LineDeletion(('triangle.py', 'line', 11)) | LineDeletion(('triangle.py', 'line', 14))"


## Patch Minification

Example: (using the automated bug fixing example)

    python -m bin.minify_patch --mode repair --config examples/scenario/triangle-rb_repair.txt --patch "LineReplacement(('triangle.rb', 'line', 11), ('triangle.rb', 'line', 1)) | LineDeletion(('triangle.rb', 'line', 12)) | LineReplacement(('triangle.rb', 'line', 25), ('triangle.rb', 'line', 27)) | LineReplacement(('triangle.rb', 'line', 6), ('triangle.rb', 'line', 6)) | LineReplacement(('triangle.rb', 'line', 3), ('triangle.rb', 'line', 3)) | LineInsertion(('triangle.rb', '_inter_line', 25), ('triangle.rb', 'line', 29)) | LineInsertion(('triangle.rb', '_inter_line', 3), ('triangle.rb', 'line', 9)) | LineInsertion(('triangle.rb', '_inter_line', 2), ('triangle.rb', 'line', 20)) | LineReplacement(('triangle.rb', 'line', 11), ('triangle.rb', 'line', 1))"


## Ablation Analysis

Example: (using the algorithm configuration example)

    python -m bin.ablation_analysis --mode config --config examples/scenario/minisat_config.txt --patch "ParamSetting(('minisat_simplified.params', 'rinc'), 3.8204404817425397) | ParamSetting(('minisat_simplified.params', 'rnd-seed'), 454275209) | ParamSetting(('minisat_simplified.params', 'luby'), 'False') | ParamSetting(('minisat_simplified.params', 'ccmin-mode'), 1)"



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

In particular:

- `minisat.patch` is applied to add comment support to MiniSAT's Dimacs parser
- `data` contains 20 instances from [SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)
- `compile.sh` simply runs the MiniSAT-provided makefile
- `test.sh` checks MiniSAT's output on 5 SAT and 5 UNSAT instances
- `run.sh` runs MiniSAT on all 20 instances
- `Solver.cc.xml` contains the AST of the MiniSAT's `core/Solver.cc` file as provided by [SrcML](https://www.srcml.org/).

To optimise running time:

    python -m bin.magpie_runtime --config examples/scenario/minisat_runtime.txt
    python -m example.magpie_runtime_xml --config examples/scenario/minisat_runtime_xml.txt

To remove any unnecessary code:

    python -m bin.magpie_bloat --config examples/scenario/minisat_debloat.txt
    python -m examples.magpie_bloat2 --config examples/scenario/minisat_debloat.txt

To optimise command line parameters:

    python -m bin.magpie_config --config examples/scenario/minisat_config.txt
    python -m examples.magpie_config_minisat --config examples/scenario/minisat_config_advanced.txt
