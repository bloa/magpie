# MAGPIE (Machine Automated General Performance Improvement via Evolution of software)

<p align="center">
  <img alt="MAGPIE logo" src="/logo_magpie.png" />
</p>

MAGPIE: your software, but more efficient!


## Getting Started

### Prerequisites

- Python 3.5+

### Getting MAGPIE

    git clone https://github.com/bloa/magpie.git

And... that's it.

<!---
### Installation

    python setup.py install

or

    python setup.py develop
--->


### Running Unit Tests

    python -m pytest test


### Citation

If you use MAGPIE for a publication, we kindly ask you to cite the following paper that describes MAGPIE's approach:

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


## First Steps

We provide two generic entry points to MAGPIE.
One dedicated to software running time optimisation, and one for automated bug fixing.
Note that for the sake of tidyness, those scripts are located in the `bin` sub-folder and thus require some Python magic speach to work out-of-the-box (e.g., `python -m bin.magpie_runtime` instead of `python magpie_runtime.py`).
Moving them or having your own entry points at top-level is expected and will simplify usage.


### Running time optimisation

    python -m bin.magpie_runtime --config examples/scenario/triangle-py_runtime.txt

Usage: TODO

#### Patch Minification

    python -m bin.minify_patch --mode runtime --config examples/scenario/triangle-py_runtime.txt --patch "LineReplacement(('triangle.py', 'line', 31), ('triangle.py', 'line', 25)) | LineDeletion(('triangle.py', 'line', 11)) | LineDeletion(('triangle.py', 'line', 14))"

Note that the `minify_patch.py` script requires knowledge of the scenario specifics.
It is written to work out-of-the-box with both "runtime" and "repair" examples, but expect having to adapt it if your write your own scenario-specific entry point.


### Automated Bug Fixing

    python -m bin.magpie_repair --config examples/scenario/triangle-rb_repair.txt

Usage: TODO

#### Patch Minification

    python -m bin.minify_patch --mode repair --config examples/scenario/triangle-rb_repair.txt --patch "LineReplacement(('triangle.rb', 'line', 11), ('triangle.rb', 'line', 1)) | LineDeletion(('triangle.rb', 'line', 12)) | LineReplacement(('triangle.rb', 'line', 25), ('triangle.rb', 'line', 27)) | LineReplacement(('triangle.rb', 'line', 6), ('triangle.rb', 'line', 6)) | LineReplacement(('triangle.rb', 'line', 3), ('triangle.rb', 'line', 3)) | LineInsertion(('triangle.rb', '_inter_line', 25), ('triangle.rb', 'line', 29)) | LineInsertion(('triangle.rb', '_inter_line', 3), ('triangle.rb', 'line', 9)) | LineInsertion(('triangle.rb', '_inter_line', 2), ('triangle.rb', 'line', 20)) | LineReplacement(('triangle.rb', 'line', 11), ('triangle.rb', 'line', 1))"


### Bloat Minimisation

    python -m bin.magpie_bloat --config examples/scenario/triangle-py_bloat.txt

Usage: TODO

See also:

    python -m examples.magpie_bloat2 --config examples/scenario/triangle-py_bloat.txt

#### Patch Minification

    python -m bin.minify_patch --mode bloat --config examples/scenario/triangle-py_bloat.txt --patch "LineDeletion(('triangle.py', 'line', 40)) | LineDeletion(('triangle.py', 'line', 20)) | LineDeletion(('triangle.py', 'line', 7)) | LineDeletion(('triangle.py', 'line', 9)) | LineDeletion(('triangle.py', 'line', 41)) | LineDeletion(('triangle.py', 'line', 6)) | LineDeletion(('triangle.py', 'line', 11)) | LineDeletion(('triangle.py', 'line', 11)) | LineDeletion(('triangle.py', 'line', 30)) | LineDeletion(('triangle.py', 'line', 2)) | LineDeletion(('triangle.py', 'line', 25)) | LineDeletion(('triangle.py', 'line', 15)) | LineDeletion(('triangle.py', 'line', 12)) | LineDeletion(('triangle.py', 'line', 14)) | LineDeletion(('triangle.py', 'line', 8)) | LineDeletion(('triangle.py', 'line', 3)) | LineDeletion(('triangle.py', 'line', 9)) | LineDeletion(('triangle.py', 'line', 10))"


### Algorithm Configuration

First, download and extract Minisat 2.2.0

    wget "http://minisat.se/downloads/minisat-2.2.0.tar.gz"
    tar xzf minisat-2.2.0.tar.gz -C example/code
    rm minisat-2.2.0.tar.gz

Then setup the MiniSAT directory with files used by MAGPIE

    cp examples/code/minisat_setup/*.sh examples/code/minisat
    cp examples/code/minisat_setup/Solver.cc.xml examples/code/minisat/simp
    cp examples/code/minisat_setup/data examples/code/minisat
    patch -d examples/code/minisat -p 1 < examples/code/minisat_setup/minisat.patch


    python -m bin.magpie_config --config examples/scenario/minisat_config.txt

Usage: TODO

See also:

    python -m examples.magpie_config_minisat --config examples/scenario/minisat_config-advanced.txt


#### Patch Minification

    python -m bin.minify_patch --mode config --config examples/scenario/minisat_config.txt --patch "ParamSetting(('minisat_simplified.params', 'rinc'), 3.8204404817425397) | ParamSetting(('minisat_simplified.params', 'rnd-seed'), 454275209) | ParamSetting(('minisat_simplified.params', 'luby'), 'False') | ParamSetting(('minisat_simplified.params', 'ccmin-mode'), 1)"


### MAGPIE's Output

TODO



### Advanced Examples

    python -m examples.magpie_repair_xml_java --config examples/scenario/triangle-java_repair_srcml.txt

    python -m examples.magpie_config_minisat --config examples/scenario/minisat_config_advanced.txt


## Acknowledgments

MAGPIE is based on [PyGGI 2.0](https://github.com/coinse/pyggi), developped at [COINSE KAIST](https://coinse.kaist.ac.kr/) in collaboration with [UCL SOLAR](https://solar.cs.ucl.ac.uk/).

Part of its development was supported by UK EPSRC Fellowship EP/P023991/1.
