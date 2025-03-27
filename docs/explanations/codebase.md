# Project Structure

```
.
├── docs
├── examples
├── magpie
├── _magpie_cache
├── _magpie_logs
├── _magpie_work
├── tests
├── LICENSE.md
├── README.md
```


## Usage Philosophy

Magpie's source code is entirely self-contained within the `magpie` directory.
You can execute this directory directly with Python, running `python3 magpie` from a terminal, which will provide you with a list of possible entry points:

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

Most entry points require a _scenario file_.
This file defines various parameters, such as:
- the location of the target software;
- how to compile, test, and run it;
- the fitness function to optimise;
- which specific files can be evolved and which transformations are considered.

The examples directory contains several example target software and scenario files for you to explore and experiment with.
For example, in `examples/triangle-py`, you'll find:
- a simple Python software (`triangle.py`, `run_triangle.py`, `test_triangle.py`)
- scripts to introduce faults (e.g., `init_slow.sh` to introduce an artificial delay)
- scenario files and corresponding diffs used by the different initialisation scripts (in `_magpie`)

```
examples/triangle-py
├── _magpie
│   ├── scenario_bloat.txt
│   ├── scenario_bug.txt
│   ├── scenario_slow.txt
│   ├── triangle_bloat.diff
│   ├── triangle_bug.diff
│   └── triangle_slow.diff
├── init_bloat.sh
├── init_bug.sh
├── init_slow.sh
├── run_triangle.py
├── test_triangle.py
└── triangle.py
```

Example usage:

    python3 magpie local_search --scenario examples/triangle-py/_magpie/scenario_slow.txt


Upon execution Magpie will create two directories:
- `_magpie_logs`, countaining execution log files, and
- `_magpie_work`, containing temporary software variants.
Additionally, `_magpie_cache` is used in the `example/minisat` example to cache a download of MiniSAT source code.
These directories can grow in size over time and can be safely deleted if not needed.


## Suggested organisation

For a streamlined Magpie setup, we suggest the following directory structure:

    .
    ├── your_software // your software to optimise
    │   └── ...
    ├── magpie        // Magpie source code
    │   └── ...
    ├── _magpie_logs  // Logs from experiments (automatically generated)
    │   └── ...
    ├── _magpie_work  // Temporary software variants (automatically generated)
    │   └── ...
    └── your_scenario.txt // Scenario file describing your experimental setup
