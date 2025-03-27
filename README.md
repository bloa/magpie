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


## Requirements

- Unix (Linux/macOS/etc; untested on Windows)
- Python 3.11+ (`master` branch)
- Python 3.8+ (`master_legacy` branch)


## Try it now!

    git clone https://github.com/bloa/magpie.git
    cd magpie
    python3 magpie local_search --scenario examples/triangle-c/_magpie/scenario_slow.txt


## Documentation

Everything you need to know about Magpie.

**Tutorials**

- [Quick start](./docs/tutorials/quick_start.md) **(start here!)**
- [Basic usage](./docs/tutorials/basic_usage.md)
- [Case study](./docs/tutorials/case_study.md)

**How-to guides**

- [Add your own fitness function](./docs/howto/write_fitness.md) _(soon)_
- [Add your own algorithm](./docs/howto/write_algo.md) _(soon)_
- [Add your own model](./docs/howto/write_model.md) _(soon)_

**Explanations**

- [Codebase structure](./docs/explanations/codebase.md)
- [Evaluation pipeline](./docs/explanations/pipeline.md)
- [Output](./docs/explanations/output.md)

**Reference guides**

- [Scenario files](./docs/reference/scenario.md)
- [Entry points](./docs/reference/entry_points.md)
- [Models](./docs/reference/models.md) _(soon)_
- [Algorithms](./docs/reference/algorithms.md) _(soon)_
- [Fitness functions](./docs/reference/fitness.md) _(soon)_


## Acknowledgements

Magpie is based on [PyGGI 2.0](https://github.com/coinse/pyggi), developed at [COINSE KAIST](https://coinse.kaist.ac.kr/) in collaboration with [UCL SOLAR](https://solar.cs.ucl.ac.uk/).  
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

