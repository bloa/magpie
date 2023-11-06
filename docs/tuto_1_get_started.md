# Get started

## Requirements

- Unix (Linux/macOS/etc; untested on Windows)
- Python 3.8+
- [Pytest](https://docs.pytest.org/) [optional: for running tests]


## Setup Magpie

Install Magpie by cloning the git repository:

    git clone https://github.com/bloa/magpie.git

As of now, Magpie is exclusively run directly from source; therefore requiring no system-wide installation.
To use it, one should write a scenario file, specifying (within other things) where the target software is located, how it is modelled, and what is the fitness function sought to be optimised.
The "examples/scenario" directory contains a number of such scenario files.


## Check installation

Run a short 60-second local search:

    python3 magpie local_search --scenario examples/scenario/triangle-cpp_runtime.txt

Show the diff corresponding to a given patch:

    python3 magpie show_patch --scenario examples/scenario/triangle-cpp_runtime.txt --patch "StmtDeletion(('triangle.cpp.xml', 'stmt', 3))"

Simplify a given patch by removing unnecessary bloat:

    python3 magpie minify_patch --scenario examples/scenario/triangle-py_runtime.txt --patch "LineInsertion(('triangle.py', '_inter_line', 31), ('triangle.py', 'line', 7)) | LineInsertion(('triangle.py', '_inter_line', 33), ('triangle.py', 'line', 21)) | LineReplacement(('triangle.py', 'line', 9), ('triangle.py', 'line', 37)) | LineInsertion(('triangle.py', '_inter_line', 4), ('triangle.py', 'line', 7))"


## Run tests

Magpie uses Pytest to run tests, located in the "tests" directory.  
To runs all tests:

    pytest
