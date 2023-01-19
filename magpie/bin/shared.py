import magpie

def setup_magpie(config):
    if 'magpie' in config:
        if 'log_dir' in config['magpie']:
            magpie.config.log_dir = config['magpie']['log_dir']
        if 'work_dir' in config['magpie']:
            magpie.config.log_dir = config['magpie']['work_dir']
        if 'local_original_copy' in config['magpie']:
            magpie.config.local_original_copy = config['magpie']['local_original_copy']
        if 'local_original_name' in config['magpie']:
            magpie.config.local_original_copy = config['magpie']['local_original_name']
        if 'output_encoding' in config['magpie']:
            magpie.config.output_encoding = config['magpie']['output_encoding']
        if 'edit_retries' in config['magpie']:
            magpie.config.edit_retries = config['magpie']['edit_retries']
        if 'default_timeout' in config['magpie']:
            magpie.config.default_timeout = float(config['magpie']['default_timeout'])
        if 'default_output' in config['magpie']:
            magpie.config.default_output = int(float(config['magpie']['default_output']))
        if 'diff_method' in config['magpie']:
            magpie.config.diff_method = config['magpie']['diff_method']

def setup_protocol(protocol, config):
    setup_search(protocol.search, config)

def setup_search(search, config):
    if 'search' in config:
        # warmup
        if 'warmup' in config['search']:
            search.config['warmup'] = int(config['search']['warmup'])
        if 'warmup_strategy' in config['search']:
            search.config['warmup_strategy'] = config['search']['warmup_strategy']
        # stopping criteria
        if 'max_steps' in config['search']:
            search.stop['steps'] = int(config['search']['max_steps'])
        if 'max_time' in config['search']:
            search.stop['wall'] = int(config['search']['max_time'])
        if 'target_fitness' in config['search']:
            search.stop['fitness'] = int(config['search']['target_fitness'])
        # cache
        if 'cache_maxsize' in config['search']:
            search.config['cache_maxsize'] = int(config['search']['cache_maxsize'])
        if 'cache_keep' in config['search']:
            search.config['cache_keep'] = float(config['search']['cache_keep'])
