# Entry Points

Magpie provides a variety of entry points to support different tasks, from search algorithms to patch inspection and utility scripts.

```
usage: python3 magpie ((magpie/){bin,scripts}/)TARGET(.py) [ARGS]...
possible TARGET:
    ablation_analysis	(magpie/bin/ablation_analysis.py)
    genetic_programming	(magpie/bin/genetic_programming.py)
    local_search    	(magpie/bin/local_search.py)
    minify_patch    	(magpie/bin/minify_patch.py)
    revalidate_patch	(magpie/bin/revalidate_patch.py)
    show_locations  	(magpie/bin/show_locations.py)
    show_patch      	(magpie/bin/show_patch.py)
    clear_xml       	(magpie/scripts/clear_xml.py)
    line_to_xml     	(magpie/scripts/line_to_xml.py)
    python_to_xml   	(magpie/scripts/python_to_xml.py)
```

## Usage

Entry points are located in subfolders and can be executed as modules using Python's `-m` option:

    python3 -m magpie.bin.local_search --scenario examples/triangle-cpp/_magpie/scenario_slow.txt

For convenience, the main `magpie` directory itself can be executed, supporting various shorthand forms:

    python3 magpie magpie/bin/local_search.py --scenario examples/triangle-cpp/_magpie/scenario_slow.txt
<!-- -->
    python3 magpie bin/local_search --scenario examples/triangle-cpp/_magpie/scenario_slow.txt
<!-- -->
    python3 magpie local_search --scenario examples/triangle-cpp/_magpie/scenario_slow.txt

If preferred, entry points can also be moved to the top level and executed directly:

    mv bin/local_search.py .
    python3 local_search.py --scenario examples/triangle-cpp/_magpie/scenario_slow.txt

## Example scenario requirements

- Python scenarios require Python 3.7+ and [pytest](https://docs.pytest.org).
- Ruby scenarios require Ruby and [minitest](https://docs.seattlerb.org/minitest/).
- Java scenarios only require Java, as both jUnit and example SrcML files are already provided.
- C scenarios require make.
- C++ scenarios require CMake.

## Main entry points

### `local_search`

Performs a local search to iteratively improve software variants by applying small modifications.

Examples:

    python3 magpie local_search --scenario examples/triangle-cpp/_magpie/scenario_slow.txt
<!-- -->
    python3 magpie local_search --scenario examples/triangle-java/_magpie/scenario_bug.txt
<!-- -->
    python3 magpie local_search --scenario examples/triangle-rb/_magpie/scenario_bug.txt
<!-- -->
    python3 magpie local_search --scenario examples/triangle-py/_magpie/scenario_bloat.txt

Arguments:
- `--scenario SCENARIO`: path to the scenario configuration file (required)
- `--algo ALGO`: local search strategy to use (optional, default: `FirstImprovement`)
- `--seed SEED`: random seed for reproducibility (optional)


### `genetic_programming`

Runs a population-based genetic programming algorithm to evolve software variants over multiple generations.

Examples:

    python3 magpie genetic_programming --scenario examples/triangle-cpp/_magpie/scenario_slow.txt
<!-- -->
    python3 magpie genetic_programming --scenario examples/triangle-java/_magpie/scenario_bug.txt
<!-- -->
    python3 magpie genetic_programming --scenario examples/triangle-rb/_magpie/scenario_bug.txt
<!-- -->
    python3 magpie genetic_programming --scenario examples/triangle-py/_magpie/scenario_bloat.txt

Arguments:
- `--scenario SCENARIO`: path to the scenario configuration file (required)
- `--algo ALGO`: local search strategy to use (optional, default: `GeneticProgrammingUniformConcat`)
- `--seed SEED`: random seed for reproducibility (optional)

### `show_patch`

Displays the diff produced by applying a Magpie patch, without performing any fitness evaluation.
Useful for quickly previewing the effect of a patch.

Examples:

    python3 magpie show_patch --scenario examples/triangle-cpp/_magpie/scenario_slow.txt --patch "SrcmlStmtDeletion(('triangle.cpp.xml', 'stmt', 3))"
<!-- -->
    python3 magpie show_patch --scenario examples/triangle-py/_magpie/scenario_slow.txt --patch "SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 23), ('triangle.py.xml', 'stmt', 15)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 7)) | SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 9), ('triangle.py.xml', 'stmt', 13)) | SrcmlStmtReplacement(('triangle.py.xml', 'stmt', 8), ('triangle.py.xml', 'stmt', 12)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 14))"

Arguments:
- `--scenario SCENARIO`: path to the scenario configuration file (required)
- `--patch PATCH`: the patch to apply, either as a string or path to a patch file (required)
- `--keep`: if set, saves a copy on disk of the mutated software for manual inspection (optional)



### `revalidate_patch`

Assesses the fitness of a given patch by applying it to the target software and running the full evaluation pipeline.
Useful for double-checking patch effectiveness or comparing patch fitness under updated conditions.

Examples:

    python3 magpie revalidate_patch --scenario examples/triangle-cpp/_magpie/scenario_slow.txt --patch "SrcmlStmtReplacement(('triangle.cpp.xml', 'stmt', 3), ('triangle.cpp.xml', 'stmt', 12))"
<!-- -->
    python3 magpie revalidate_patch --scenario examples/triangle-py/_magpie/scenario_slow.txt --patch "SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 23), ('triangle.py.xml', 'stmt', 15)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 7)) | SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 9), ('triangle.py.xml', 'stmt', 13)) | SrcmlStmtReplacement(('triangle.py.xml', 'stmt', 8), ('triangle.py.xml', 'stmt', 12)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 14))"

Arguments:
- `--scenario SCENARIO`: path to the scenario configuration file (required)
- `--patch PATCH`: the patch to evaluate, either as a string or path to a patch file (required)


### `minify_patch`

Processes the individual mutations of a given patch in order to obtain a leaner, cleaner, shorter, and more reliable patch.

The patches generated by Magpie are seldom optimal and often contain bloat.
In practice, every individual edit is separately evaluated and ranked, and a new patch is constructed by reintroducing every edit in order, only accepting it on fitness improvement.
This new patch (or the original, in rare cases in which the rebuild is unsuccessful) is then made as small as possible by trying to remove every edit one by one.
Note that noise in fitness measurement may lead to non-optimal patch being returned.

Example:

    python3 magpie minify_patch --scenario examples/triangle-py/_magpie/scenario_slow.txt --patch "SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 23), ('triangle.py.xml', 'stmt', 15)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 7)) | SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 9), ('triangle.py.xml', 'stmt', 13)) | SrcmlStmtReplacement(('triangle.py.xml', 'stmt', 8), ('triangle.py.xml', 'stmt', 12)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 14))"

Arguments:
- `--scenario SCENARIO`: path to the scenario configuration file (required)
- `--patch PATCH`: the patch to evaluate, either as a string or path to a patch file (required)


### `ablation_analysis`

In contrary to the `minify_patch.py` entry point, which aims to minimise patch size, the `ablation_analysis.py` entry point aims to highlight the individual contribution of every edit in the overall fitness improvement.
A patch can either be provided directly or as a path to a file containing the patch representation.

Example:

    python3 magpie ablation_analysis --scenario examples/triangle-py/_magpie/scenario_slow.txt --patch "SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 23), ('triangle.py.xml', 'stmt', 15)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 7)) | SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 9), ('triangle.py.xml', 'stmt', 13)) | SrcmlStmtReplacement(('triangle.py.xml', 'stmt', 8), ('triangle.py.xml', 'stmt', 12)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 14))"

Arguments:
- `--scenario SCENARIO`: path to the scenario configuration file (required)
- `--patch PATCH`: the patch to evaluate, either as a string or path to a patch file (required)


### `show_locations`

Displays the available modification locations defined for the target software.
Useful to inspect which parts of the code are eligible for edits according to the scenario.


Examples:

    python3 magpie show_locations --scenario examples/triangle-rb/_magpie/scenario_bug.txt
<!-- -->
    python3 magpie show_locations --scenario examples/triangle-rb/_magpie/scenario_bug.txt --filename triangle.rb --tag line

Arguments:
- `--scenario SCENARIO`: path to the scenario configuration file (required)
- `--filename NAME`: restricts the output to a specific file (optional)
- `--tag TAG`: restricts the output to locations of a specific kind (e.g., `line`, `stmt`, etc.) (optional)


## Utility Scripts

### `line_to_xml`

Parses a regular source file and outputs its line-based representation in XML format.

Example:

    python3 magpie scripts/line_to_xml --file examples/triangle-java/Triangle.java

Arguments:
- `--file FILE`: path to the source file to parse (required)


### `python_to_xml`

Parses a Python source file and generates a corresponding XML representation using Python's native AST tools.

Examples:

    python3 magpie scripts/python_to_xml examples/triangle-py/triangle.py
<!-- -->
    cat examples/triangle-py/triangle.py | python3 magpie scripts/python_to_xml

Arguments:
- `--file FILE`: path to the Python source file to parse (required)


### `clear_xml`

Takes an XML file as input and outputs its contents with all XML tags stripped, leaving only the raw content.

Examples:

    python3 magpie scripts/clear_xml examples/triangle-c/_magpie/triangle_bug.c.xml
    <!-- -->
    cat examples/triangle-py/triangle.py | python3 magpie scripts/python_to_xml.py | python3 magpie scripts/clear_xml.py
