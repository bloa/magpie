import importlib

import magpie

def setup_magpie(config):
    if 'magpie' in config:
        if 'import' in config['magpie']:
            file_path = config['magpie']['import']
            module_path = file_path.rstrip('.py').lstrip('./').replace('/', '.')
            importlib.import_module(module_path)
        if 'log_dir' in config['magpie']:
            magpie.config.log_dir = config['magpie']['log_dir']
        if 'work_dir' in config['magpie']:
            magpie.config.log_dir = config['magpie']['work_dir']
        if 'local_original_copy' in config['magpie']:
            v = config['magpie']['local_original_copy']
            if v.lower() in ['true', 't', '1']:
                       magpie.config.local_original_copy = True
            elif v.lower() in ['false', 'f', '0']:
                       magpie.config.local_original_copy = False
            else:
                raise ValueError('[magpie] local_original_copy should be Boolean')
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
