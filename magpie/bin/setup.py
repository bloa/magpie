import importlib
import random

import magpie

def setup(config):
    # [magpie]
    sec = config['magpie']
    if val := sec['import']:
        importlib.import_module(val.rstrip('.py').lstrip('./').replace('/', '.'))
    if val := sec['seed']:
        random.seed(sec['seed'])

    magpie.config.log_dir = sec['log_dir']
    magpie.config.work_dir = sec['work_dir']

    tmp = sec['local_original_copy'].lower()
    if tmp in ['true', 't', '1']:
        magpie.config.local_original_copy = True
    elif tmp in ['false', 'f', '0']:
        magpie.config.local_original_copy = False
    else:
        raise ValueError('[magpie] local_original_copy should be Boolean')
    magpie.config.local_original_copy = sec['local_original_name']
    magpie.config.output_encoding = sec['output_encoding']
    magpie.config.edit_retries = int(sec['edit_retries'])
    magpie.config.default_timeout = float(sec['default_timeout'])
    magpie.config.default_output = int(float(sec['default_output']))
    magpie.config.diff_method = sec['diff_method']
