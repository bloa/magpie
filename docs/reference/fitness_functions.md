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
