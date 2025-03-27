# Project Structure

## Usage Philosophy

Magpie's source code is entirely self-contained in a single directory ("magpie").
This directory contains a magic `__main__.py` Python file and thus is directly executable.
Therefore, simply running `python3 magpie` from a terminal (in the parent directory) will provide you with a list of possible entry points:

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

To use Magpie, you typically need to provide a _scenario file_ describing, within many other things, where the target software is located, how it is used, how it should be modelled, and what is the fitness function to optimise.
Upon execution Magpie will create two directories, `_magpie_logs` and `_magpie_work`, respectively containing execution log files and temporary software variants.
These two directories may quickly fill up space and can safely be deleted.

Ultimately, the typical Magpie setup will involve the following structure:

    .
    ├── code // Software to optimise
    │   └── ...
    ├── magpie // Magpie source code directory
    │   └── ...
    ├── _magpie_logs // Experiments' log files (automatically generated)
    │   └── ...
    ├── _magpie_work // Temporary software variants (automatically generated)
    │   └── ...
    └── scenario.txt // Experiments' setup file
