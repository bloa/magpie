default_scenario = {
    # [magpie] section
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
        'default_lengthout': 1e4,
        'diff_method': 'unified',
        'trust_local_filesystem': True,
    },

    # [magpie.log] section
    'magpie.log': {
        'color_output': True,
        'format_info': '{counter:<7} {status:<20} {best}{fitness} ({ratio}) [{size}] {cached} {log}',
        'format_debug': 'patch({counter})="{patch}"',
        'format_fitness': '{:.2f}',
        'format_ratio': '{:.2%%}',
    },

    # [software] section
    'software': {
        'path': '',
        'target_files': '',
        'software': 'BasicSoftware',
        'model_rules': """
*.params : ConfigFileParamsModel
*.xml : SrcmlModel
* : LineModel""",
        'model_config': """
*.params : [params]
*.xml : [srcml]""",
        'init_cmd': '',
        'init_timeout': '60',
        'init_lengthout': '-1',
        'setup_cmd': '',
        'setup_timeout': '',
        'setup_lengthout': '',
        'compile_cmd': '',
        'compile_timeout': '',
        'compile_lengthout': '',
        'test_cmd': '',
        'test_timeout': '',
        'test_lengthout': '',
        'run_cmd': '',
        'run_timeout': '',
        'run_lengthout': '',
        'batch_timeout': '',
        'batch_lengthout': '',
        'batch_bin_fitness_strategy': 'aggregate', # aggregate ; sum ; average ; median ; q10 ; q25 ; q75 ; q90
        'batch_fitness_strategy': 'sum', # sum ; average ; median
    },

    # [srcml] section
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

    # [params] section
    'params': {
        'timing': 'test run',
        'cli_prefix': '--',
        'cli_glue': '=',
        'cli_boolean': 'show', # show ; hide ; prefix
        'cli_boolean_prefix_true': '',
        'cli_boolean_prefix_false': 'no-',
        'cli_none': 'hide', # show ; hide
        'silent_prefix': '@',
        'silent_suffix': '$',
    },

    # [search] section
    'search': {
        'protocol': 'BasicProtocol',
        'algorithm': '',
        'possible_edits': '',
        'warmup': 3,
        'warmup_strategy': 'last',
        'max_steps': '',
        'max_time': '',
        'target_fitness': '',
        'cache_maxsize': 100,
        'cache_keep': 0.2,
        'batch_instances': '', # separated by "|" see also "file:"
        'batch_shuffle': True,
        'batch_bin_shuffle': False,
        'batch_sample_size': 1,
    },

    # [search.ls] section
    'search.ls': {
        'delete_prob': 0.5,
        'max_neighbours': '',
        'when_trapped': 'continue',
        'accept_fail': False, # RandomWalk only
        'tabu_length': 10, # TabuSearch only
    },

    # [search.gp] section
    'search.gp': {
        'pop_size': 10,
        'delete_prob': 0.5,
        'offspring_elitism': 0.1,
        'offspring_crossover': 0.5,
        'offspring_mutation': 0.4,
        'uniform_rate': 0.5, # GeneticProgrammingUniformConcat and GeneticProgrammingUniformInter only
        'batch_reset': True,
    },

    # [search.minify] section
    'search.minify': {
        'do_cleanup': True,
        'do_rebuild': True,
        'do_simplify': True,
        'round_robin_limit': 3,
    },
}
