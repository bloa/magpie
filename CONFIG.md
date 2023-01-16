# Configuration File

Magpie's default entry points (see [USAGE.md](/USAGE.md)) all use configuration files to quickly fine-tune execution.
There are three main sections, detailed below.

Note that when writing custom entry points, configuration files may be completely bypassed (see [`magpie/bin/shared.py`](magpie/bin/shared.py)).


## `[magpie]`

Default values:

    [magpie]
    log_dir = '_magpie_logs'
    work_dir = '_magpie_work'
    local_original_copy = False
    local_original_name = '__original__'
    output_encoding = 'ascii'
    edit_retries = 10
    default_timeout = 30
    default_output = 1e4
    diff_method = 'unified'

- `log_dir`: the folder in which logs, diffs, and patches are saved after execution
- `work_dir`: the folder in which mutated software variants are cloned, modified, compiled, and run
- `local_original_copy`: whether an intermediary copy of the original software is also cloned in `work_dir` (useful e.g. in cluster to clone everything in `/tmp`.
- `local_original_name`: the name of the intermerdiary copy in `work_dir` (only if `local_original_copy` is `True`)
- `output_encoding`: the character encoding used to decode the target software's stdout/stderr
- `edit_retries`: how many invalid edits Magpie tries to generate in a row before completely giving up on .
- `default_timeout`: maximum execution time Magpie waits before discarding a software variant (used if `compile_timeout`, `test_timeout`, or `run_timeout` is not specified in `[software]`)
- `default_output`: maximum output file size Magpie records before discarding a software variant (used if `compile_output`, `test_output`, or `run_output` is not specified in `[software]`)
- `diff_method`: type of diff format (either "unified" or "context")


## `[software]`

Default values:

    [software]
    path = 
    target_files =
    compile_cmd = None
    compile_timeout = None
    compile_output = None
    test_cmd = None
    test_timeout = None
    test_output = None
    run_cmd = None
    run_timeout = None
    run_output = None

- `path`: the original software folder cloned during execution
- `target_files`: the files (relatively to `path`) targeted by Magpie
- `compile_cmd`: command line to execute during the compilation step (or "None", in which case it is skipped)
- `compile_timeout`: maximum execution time during the compilation step (or "None", in which case `default_timeout` from `[magpie]` is used)
- `compile_output`: maximum output file size during the compilation step (or "None", in which case `default_output` from `[magpie]` is used)
- `test_cmd`
- `test_timeout`
- `test_output`
- `run_cmd`
- `run_timeout`
- `run_output`


# `[search]`

Default values:

    [search]
    warmup = 3
    warmup_strategy = 'last'
    max_steps = None
    max_time = None
    target_fitness = None
    cache_maxsize = 40
    cache_keep = 0.2

- `warmup`: number of initial evaluation to consider
- `warmup_strategy`: which warmup fitness value to use (possible: "last", "min", "max", "mean", "median")
- `max_steps`: maximum number of steps before Magpie terminates
- `max_time`: maximum execution time before Magpie terminates
- `target_fitness`: if not "None", Magpie terminates as soon as a smaller or equal fitness value is found
- `cache_maxsize`: maximum number of cached run results (use 0 to disable; not recommended)
- `cache_keep`: percentage of cached run results kept when `cache_maxsize` is reached
