# Configuration File

Magpie's default entry points require a scenario file in the [INI format](https://en.wikipedia.org/wiki/INI_file).
Examples of such files can be found in the `examples/scenario` folder.
We detail in the following the different section, properties, and default values used by Magpie.


## `[magpie]`

Default values:

    [magpie]
    import =
    log_dir = '_magpie_logs'
    work_dir = '_magpie_work'
    local_original_copy = False
    local_original_name = '__original__'
    output_encoding = 'ascii'
    edit_retries = 10
    default_timeout = 30
    default_output = 1e4
    diff_method = 'unified'

- `import`: the path of an optional Python file to import
- `log_dir`: the folder in which logs, diffs, and patches are saved after execution
- `work_dir`: the folder in which mutated software variants are cloned, modified, compiled, and run
- `local_original_copy`: whether an intermediary copy of the original software is also cloned in `work_dir` (useful e.g. in cluster to clone everything in `/tmp`.
- `local_original_name`: the name of the intermerdiary copy in `work_dir` (only if `local_original_copy` is `True`)
- `output_encoding`: the character encoding used to decode the target software's stdout/stderr
- `edit_retries`: how many invalid edits Magpie tries to generate in a row before completely giving up on .
- `default_timeout`: maximum execution time Magpie waits before discarding a software variant (used if `compile_timeout`, `test_timeout`, or `run_timeout` is not specified in `[software]`)
- `default_output`: maximum output file size Magpie records before discarding a software variant (used if `compile_output`, `test_output`, or `run_output` is not specified in `[software]`)
- `diff_method`: type of diff format (either ["unified"](https://www.gnu.org/software/diffutils/manual/html_node/Example-Unified.html) or ["context"](https://www.gnu.org/software/diffutils/manual/html_node/Example-Context.html))


## `[srcml]`

Default values:

    [srcml]
    rename =
        stmt: break continue decl_stmt do expr_stmt for goto if return switch while
        number: literal_number
    focus = block stmt operator_comp operator_arith number
    internodes = block
    process_pseudo_blocks = True
    process_literals = True
    process_operators = True

- `rename`: a multi-line dictionary of renaming rules.
  E.g., all `<break>` and `<continue>` tags will be renamed `<stmt>`.
  This is to ensures consistency, as Magpie's default edits only apply to identical XML tags.
- `focus`: the list of tags to keep in the file (all other tags are internally discarded)
- `internodes`: a list of tags to process for future node insertion.
  E.g., `internodes = block` will create the `_inter_block` insertion points.
- `process_pseudo_blocks`: automatically inserts curly braces around otherwise braceless blocks
  (e.g., single-line if statement).
- `process_literals`: rename `<literal>` tags according to their `type` attribute.
  E.g., `<literal type="number">' to `<literal_number>`.
- `process_operators`: rename `<operator>` tags into `<operator_comp>`, `<operator_arith>` or `<operator_misc>` according to their text contents.


## `[software]`

Default values:

    [software]
    path =
    target_files =
    engine_rules =
        *.params : ConfigFileParamsEngine
        *.xml : SrcmlEngine
        * : LineEngine
    possible_edits =
    setup_cmd = None
    setup_timeout = None
    setup_output = None
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
- `target_files`: the list of files (relatively to `path`) targeted by Magpie
- `engine_rules`: the list of rules used to determine how target files are internally represented
- `possible_edits`: the list of edits available to the search process
- `setup_cmd`: command line to execute during the setup step (or "" or "None", in which case it is skipped)
- `setup_timeout`: maximum execution time during the setup step (or "" or "None", in which case `default_timeout` from `[magpie]` is used)
- `setup_output`: maximum output file size during the setup step (or "" or "None", in which case `default_output` from `[magpie]` is used)
- `compile_cmd`
- `compile_timeout`
- `compile_output`
- `test_cmd`
- `test_timeout`
- `test_output`
- `run_cmd`
- `run_timeout`
- `run_output`

Note that both `target_files` and `possible edits` lists are newline-separated; the first line (after the `=`) may be empty, any subsequent line must start with a space.
Typical examples:

    possible_edits =
        LineReplacement
        LineInsertion
        LineDeletion

    possible_edits = ParamSetting


# `[search]`

Default values:

    [search]
    warmup = 3
    warmup_strategy = last
    max_steps = None
    max_time = None
    target_fitness = None
    cache_maxsize = 40
    cache_keep = 0.2

- `warmup`: number of initial evaluation to consider
- `warmup_strategy`: which warmup fitness value to use (possible: `last`, `min`, `max`, `mean`, `median`)
- `max_steps`: maximum number of steps before Magpie terminates
- `max_time`: maximum execution time before Magpie terminates
- `target_fitness`: if not `None`, Magpie terminates as soon as a smaller or equal fitness value is found
- `cache_maxsize`: maximum number of cached run results (use 0 to disable; not recommended)
- `cache_keep`: percentage of cached run results kept when `cache_maxsize` is reached


Local search parameters:

    delete_prob = 0.5
    max_neighbours = None
    when_trapped = continue
    accept_fail = False # RandomWalk only
    tabu_length = 10 # TabuSearch only

- `delete_prob`: probability to delete a random edit instead of generating a new one
- `max_neighbours`: number of neighbours the local search can generate without acceptance (default = 20 for BestImprovement)
- `when_trapped`: what to do when `max_neighbours` neighbours are rejected in a row (possible: `continue`, `stop`)
- `accept_fail`: enable walking through fitness-less software variants (RandomWalk only)
- `tabu_length`: length of the tabu list of software variants (TabuSearch only)

Genetic programming parameters:

    pop_size = 10
    delete_prob = 0.5
    offspring_elitism = 0.1
    offspring_crossover = 0.5
    offspring_mutation = 0.4
    uniform_rate = 0.5 # GeneticProgrammingUniformConcat and GeneticProgrammingUniformInter only

- `pop_size`: population size
- `delete_prob`: probability to delete a random edit instead of generating a new one
- `offspring_elitism`: proportion of the old population carried over
- `offspring_crossover`: proportion of the old population crossed over with random valid parent
- `offspring_mutation`: proportion of the old population mutated
- `uniform_rate`: percentage of edits originating from the first parent
