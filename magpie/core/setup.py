import importlib
import pathlib
import random

import magpie.settings

from .errors import ScenarioError


def pre_setup(config):
    # [magpie] section
    sec = config['magpie']
    if val := sec['import']:
        for module in val.split():
            try:
                s = pathlib.Path(config['software']['path']) /  module
                importlib.import_module(s.rstrip('.py').lstrip('./').replace('/', '.'))
            except ModuleNotFoundError:
                importlib.import_module(val.rstrip('.py').lstrip('./').replace('/', '.'))
    if val := sec['seed']:
        random.seed(int(val))
    else:
        val = random.randint(0, int(1e16))
        random.seed(val)
        sec['seed'] = str(val)

def setup(config):
    # [magpie] section
    sec = config['magpie']
    magpie.settings.log_dir = sec['log_dir']
    magpie.settings.work_dir = sec['work_dir']

    tmp = sec['local_original_copy'].lower()
    if tmp in ['true', 't', '1']:
        magpie.settings.local_original_copy = True
    elif tmp in ['false', 'f', '0']:
        magpie.settings.local_original_copy = False
    else:
        msg = '[magpie] local_original_copy should be Boolean'
        raise ScenarioError(msg)
    magpie.settings.local_original_copy = sec['local_original_name']
    magpie.settings.output_encoding = sec['output_encoding']
    magpie.settings.edit_retries = int(sec['edit_retries'])
    magpie.settings.default_timeout = float(sec['default_timeout'])
    magpie.settings.default_lengthout = int(float(sec['default_lengthout']))
    magpie.settings.diff_method = sec['diff_method']
    val = sec['trust_local_filesystem'].lower()
    if val in ['true', 't', '1']:
        magpie.settings.trust_local_filesystem = True
    elif val in ['false', 'f', '0']:
        magpie.settings.trust_local_filesystem = False
    else:
        msg = '[magpie] trust_local_filesystem should be Boolean'
        raise ScenarioError(msg)
