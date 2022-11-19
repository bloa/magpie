# Magpie (Machine Automated General Performance Improvement via Evolution of software)

<p align="center">
  <img alt="MAGPIE logo" src="./logo_magpie.png" />
</p>

Magpie: your software, but more efficient!

## Introduction

Magpie is a tool for automated software improvement.
It implements [MAGPIE](#citation), using the genetic improvement methodology to traverse the search space of different software variants to find improved software.

Magpie provides support for improvement of both functional (automated bug fixing) and non-functional (e.g., execution time) properties of software.  
Two types of language-agnostic source code representations are supported: line-by-line, and XML trees.
For the latter we recommend the [srcML](https://www.srcml.org/) tool with out-of-the-box support for C/C++/C# and Java.  
Finally, Magpie also enables parameter tuning and algorithm configuration, both independently and concurrently of the source code search process.

## Getting Started

### Prerequisites

- Python 3.5+
- [Astor](https://astor.readthedocs.io/) [optional: for native Python AST manipulation]
- [Pytest](https://docs.pytest.org/) [optional: for running tests]

### Getting Magpie

    git clone https://github.com/bloa/magpie.git

And... that's it.

### Running Unit Tests

    python -m pytest test

### Citation

If you use Magpie for a publication, we kindly ask you to cite the following paper that describes MAGPIE's approach:

```
@article{blot:2022:corr_1,
  author    = {Aymeric Blot and
               Justyna Petke},
  title     = {{MAGPIE:} {M}achine Automated General Performance Improvement via Evolution of Software},
  journal   = {Computing Research Repository},
  volume    = {abs/2208.02811},
  url       = {https://arxiv.org/abs/2208.02811},
  year      = {2022},
}
```


## Usage Philosophy

Magpie's source code is entirely self-contained in the `magpie` folder.
In order to conduct experiments in the most convenient way, we recommend the following setup, starting from an empty directory:

    .
    ├── code // The software to optimise
    │   └── ...
    ├── magpie // Magpie source code (not the entire git repo)
    │   └── ...
    ├── _magpie_logs // Experiments' log files (automatically generated)
    │   └── ...
    ├── _magpie_work // Temporary software variants (automatically generated)
    │   └── ...
    ├── run_optimise.py // Customised entry point
    ├── run_validate.py // Customised entry point
    └── scenario.txt // Experiments' setup file

The `_magpie_logs` folder will contain all log files (outputs, patches, diffs, etc) created by Magpie, whilst the `_magpie_work` folder will contain temporary software variants.
Both folders are automatically generated.

We provide (in `bin`) several generic optimisation entry points, targeting running time optimisation, automated bug fixing, bloat minimisation, and algorithm configuration.
We also provide several validation entry points, including simple fitness reassessment of the final patch, patch minimisation, or ablation analysis.

These are discussed in more detailed in [USAGE.md](/USAGE.md).

In addition, we also provide more complex examples in [ADVANCED.md](/ADVANCED.md).


## Acknowledgments

Magpie is based on [PyGGI 2.0](https://github.com/coinse/pyggi), developped at [COINSE KAIST](https://coinse.kaist.ac.kr/) in collaboration with [UCL SOLAR](https://solar.cs.ucl.ac.uk/).

Part of its development was supported by UK EPSRC Fellowship EP/P023991/1.
