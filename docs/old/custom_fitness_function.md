# User-provided fitness function

One can easily specify a custom fitness function by writing it directly in Python.

First, create a Python file (say, `my_software.py`) in the file tree of either your target software or Magpie main directory.

    .
    ├── code // Software to optimise
    │   ├── my_software.py // <- put it either here
    │   └── ...
    ├── magpie // Magpie source code (not the entire git repository)
    ├── _magpie_logs // Experiments' log files (automatically generated)
    ├── _magpie_work // Temporary software variants (automatically generated)
    ├── my_software.py // <- or else put it there
    └── scenario.txt // Experiments' setup file

Then add it in your scenario file, with `[magpie] import`.

    import = my_software.py

You can import multiple files by separating them either by spaces or newlines (caution: indentation is important).

For example,

    import = my_software.py my_algorithm.py

or

    import =
        my_software.py
        my_algorithm.py

Then, create a new class inheriting `magpie.core.BasicSoftware`; you will want to define a new `process_run_exec` method.
This method is called after the "run" execution and takes two parameters: `run_result` (a `magpie.core.RunResult` object) pertaining to the overall variant evaluation, and `exec_result` (a `magpie.core.ExecResult` object) that encodes the execution return status, STDOUT, and STDERR.
It should either leave `run_result.status` to `"SUCCESS"` and set `run_result.fitness` to a float, or set the error type to `run_result.status`.

In the following example, we define a `MySoftware` class for which fitness is directly read from STDOUT.

```
import magpie
from magpie.core import BasicSoftware

class MySoftware(BasicSoftware):
    def process_run_exec(self, run_result, exec_result):
        stdout = exec_result.stdout.decode(magpie.config.output_encoding)
        try:
            run_result.fitness = float(stdout)
        except ValueError:
            run_result.status = 'PARSE_ERROR'
```

Finally, you need to expose this class to Magpie by adding it to `magpie.core.known_software` in the script file, and lastly specify it in the scenario file in `[software] software`.

Final code: (`my_software.py` at the root of the target software file tree)

```
import magpie

class MySoftware(magpie.core.BasicSoftware):
    def process_run_exec(self, run_result, exec_result):
        stdout = exec_result.stdout.decode(magpie.config.output_encoding)
        try:
            run_result.fitness = float(stdout)
        except ValueError:
            run_result.status = 'PARSE_ERROR'

magpie.core.known_software.append(MySoftware)
```

Modifications to the scenario file:

```
[magpie]
import = my_scenario.py

[software]
software = MySoftware
```
