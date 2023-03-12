default_config = {
    # [magpie]
    'magpie': {
        'import': '',
        'seed': '',
        'log_dir': '_magpie_logs',
        'work_dir': '_magpie_work',
        'local_original_copy': False,
        'local_original_name': '__original__',
        'output_encoding': 'ascii',
        'edit_retries': 10,
        'default_timeout': 30,
        'default_output': 1e4,
        'diff_method': 'unified',
    },

    # [software]
    'software': {
        'path': '',
        'target_files': '',
        'program': 'BasicProgram',
        'engine_rules': """
*.params : ConfigFileParamsEngine
*.xml : SrcmlEngine
* : LineEngine""",
        'engine_config': """
*.params : [params]
*.xml : [srcml]""",
        'setup_cmd': '',
        'setup_timeout': '',
        'setup_output': '',
        'compile_cmd': '',
        'compile_timeout': '',
        'compile_output': '',
        'test_cmd': '',
        'test_timeout': '',
        'test_output': '',
        'run_cmd': '',
        'run_timeout': '',
        'run_output': '',
    },

    # [srcml]
    'srcml': {
        'rename': """
stmt: break continue decl_stmt do expr_stmt for goto if return switch while
number: literal_number""",
        'focus': 'block stmt operator_comp operator_arith number',
        'internodes': 'block',
        'process_pseudo_blocks': True,
        'process_literals': True,
        'process_operators': True,
    },

    # [params]
    'params': {
        'timing': "test run",
        'cli_prefix': "--",
        'cli_glue': "=",
        'cli_boolean': 'show', # show ; hide ; prefix
        'cli_boolean_prefix_true': '',
        'cli_boolean_prefix_false': 'no-',
        'silent_prefix': '@',
        'silent_suffix': '$',
    },

    # [search]
    'search': {
        'protocol': 'BasicProtocol',
        'algorithm': '',
        'possible_edits': 'LineInsertion LineDeletion LineReplacement',
        'warmup': 3,
        'warmup_strategy': 'last',
        'max_steps': '',
        'max_time': '',
        'target_fitness': '',
        'cache_maxsize': 40,
        'cache_keep': 0.2,
    },

    # [search.ls]
    'search.ls': {
        'delete_prob': 0.5,
        'max_neighbours': '',
        'when_trapped': 'continue',
        'accept_fail': False, # RandomWalk only
        'tabu_length': 10, # TabuSearch only
    },

    # [search.gp]
    'search.gp': {
        'pop_size': 10,
        'delete_prob': 0.5,
        'offspring_elitism': 0.1,
        'offspring_crossover': 0.5,
        'offspring_mutation': 0.4,
        'uniform_rate': 0.5, # GeneticProgrammingUniformConcat and GeneticProgrammingUniformInter only
    },
}
