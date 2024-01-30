# Magpie (Machine Automated General Performance Improvement via Evolution of software)

<p align="center">
  <img alt="MAGPIE logo" src="./docs/logo_magpie.png" />
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

**Requirements:**

- Python 3.8+
- [Pytest](https://docs.pytest.org/) [optional: for running tests]

Install Magpie by cloning the git repository:

    git clone https://github.com/bloa/magpie.git

Optionally, run Magpie's unit tests:

    pytest

Try one of the following examples:

    python3 magpie local_search --scenario examples/triangle-cpp/_magpie/scenario_slow.txt
<!-- -->
    python3 magpie local_search --scenario examples/triangle-java/_magpie/scenario_bug.txt
<!-- -->
    python3 magpie show_patch --scenario examples/triangle-cpp/_magpie/scenario_slow.txt --patch "SrcmlStmtDeletion(('triangle.cpp.xml', 'stmt', 3))"
<!-- -->
    python3 magpie minify_patch --scenario examples/triangle-py/_magpie/scenario_slow.txt --patch "SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 35), ('triangle.py.xml', 'stmt', 22)) | SrcmlStmtReplacement(('triangle.py.xml', 'stmt', 7), ('triangle.py.xml', 'stmt', 1)) | SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 24), ('triangle.py.xml', 'stmt', 6)) | SrcmlStmtInsertion(('triangle.py.xml', '_inter_block', 15), ('triangle.py.xml', 'stmt', 21)) | SrcmlStmtDeletion(('triangle.py.xml', 'stmt', 8))"


## Documentation

- [User Guide](./docs/guide.md)
- [Tutorial](./docs/tutorial.md)
- [Scenario Files](./docs/scenario.md)
- [Algorithm Configuration](./docs/algoconfig.md)


## Acknowledgements

Magpie is based on [PyGGI 2.0](https://github.com/coinse/pyggi), developped at [COINSE KAIST](https://coinse.kaist.ac.kr/) in collaboration with [UCL SOLAR](https://solar.cs.ucl.ac.uk/).  
Part of its development was supported by UK EPSRC Fellowship EP/P023991/1.

If you use Magpie for a publication, we kindly ask you to cite the following [ArXiV paper](https://arxiv.org/abs/2208.02811) that describes MAGPIE's approach:

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

