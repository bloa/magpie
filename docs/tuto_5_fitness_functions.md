# Fitness functions

Magpie generic entry points natively support many fitness schemes.

Out-of-the-box:
- **time**
- **bloat_lines**
- **bloat_words**
- **bloat_chars**

Require specific outputs:
- **repair**
- **posix_time**
- **perf_time**
- **perf_instructions**
- **output**


## Native fitness functions

### Execution time

With `time` the fitness value is the time taken to execute the "run" command, as seen from Magpie's main Python process.

With `posix_time` Magpie checks STDERR for a string matching `real XXX`.
A simple way to get a compatible output is to prepend the "run" command with a call to GNU time.
For example, in your scenario file try replacing

    run_cmd = my_command --with arguments

with

    run_cmd = /usr/bin/time -p my_command --with arguments


However, note that the GNU time command is not very precise.

Similarly, with `perf_time` Magpie checks STDERR for a string matching `XXX seconds time elapsed`.
It is meant to be used with Linux-based distributions shipping [perf](https://perf.wiki.kernel.org/).
Using the same example as above, try replacing your run command with

    run_cmd = perf stat my_command --with arguments

Finally, when available we recommend using perf's instruction count instead of the time elapsed.
With `perf_instructions` Magpie checks STDERR for a string matching `XXX instructions` (commas thousands separators are ignored).
Again, simply prepend your run command with `perf stat`.


### Bug fixing

With `repair` the "run" command is bypassed.
Instead, during the test step, Magpie checks STDOUT for specific strings to determine the number of failing test cases and the number of total test cases.
For example, Magpie will search for the strings `Failures: XXX` and `Tests run: XXX` to support JUnit.
Note that Magpie computes the _percentage_ of failing tests to avoid misleading improvements (e.g., the test harness crashing and only reporting the first, and therefore only, test fail).
Magpie ships with native support for JUnit (Java), pytest (Python), and minitest (Ruby).


### Bloat

With `bloat_lines`, `bloat_words`, `bloat_chars` the "run" command is bypassed.
Instead, Magpie directly reads each target file and compute the total number of respectively lines, words, and characters.


### User-provided fitness value

With `output` Magpie checks STDOUT for the generic `MAGPIE_FITNESS: XXX` string.


## User-provided fitness function

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
