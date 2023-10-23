import importlib
import os
import random

import magpie

def pre_setup(config):
    # [magpie]
    sec = config['magpie']
    if val := sec['import']:
        for module in val.split():
            try:
                s = os.path.join(config['software']['path'], module)
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
    # [magpie]
    sec = config['magpie']
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
    magpie.config.default_lengthout = int(float(sec['default_lengthout']))
    magpie.config.diff_method = sec['diff_method']
    val = sec['trust_local_filesystem'].lower()
    if val in ['true', 't', '1']:
        magpie.config.trust_local_filesystem = True
    elif val in ['false', 'f', '0']:
        magpie.config.trust_local_filesystem = False
    else:
        raise ValueError('[magpie] trust_local_filesystem should be Boolean')

    # [srcml]
    sec = config['srcml']
    val = sec['process_pseudo_blocks']
    if val.lower() in ['true', 't', '1']:
        magpie.xml.SrcmlModel.PROCESS_PSEUDO_BLOCKS = True
    elif val.lower() in ['false', 'f', '0']:
        magpie.xml.SrcmlModel.PROCESS_PSEUDO_BLOCKS = False
    else:
        raise ValueError('Invalid config file: "[srcml] process_pseudo_blocks" should be Boolean')
    val = sec['process_literals']
    if val.lower() in ['true', 't', '1']:
        magpie.xml.SrcmlModel.PROCESS_LITERALS = True
    elif val.lower() in ['false', 'f', '0']:
        magpie.xml.SrcmlModel.PROCESS_LITERALS = False
    else:
        raise ValueError('Invalid config file: "[srcml] process_literals" should be Boolean')
    val = sec['process_operators']
    if val.lower() in ['true', 't', '1']:
        magpie.xml.SrcmlModel.PROCESS_OPERATORS = True
    elif val.lower() in ['false', 'f', '0']:
        magpie.xml.SrcmlModel.PROCESS_OPERATORS = False
    else:
        raise ValueError('Invalid config file: "[srcml] process_operators" should be Boolean')
    magpie.xml.SrcmlModel.INTERNODES = set(sec['internodes'].split())
    h = {}
    for rule in sec['rename'].split("\n"):
        if rule.strip(): # discard potential initial empty line
            try:
                k, v = rule.split(':')
            except ValueError:
                raise ValueError('badly formated rule: "{}"'.format(rule))
            h[k] = set(v.split())
    magpie.xml.SrcmlModel.TAG_RENAME = h
    magpie.xml.SrcmlModel.TAG_FOCUS = set(sec['focus'].split())

    # [params]
    sec = config['params']
    tmp = sec['timing'].split()
    if any((val := timing) not in ['setup', 'compile', 'test', 'run'] for timing in tmp):
        raise ValueError('illegal timing value: {}'.format(val))
    magpie.params.AbstractParamsModel.TIMING = tmp
    magpie.params.AbstractParamsModel.CLI_PREFIX = sec['cli_prefix']
    magpie.params.AbstractParamsModel.CLI_GLUE = sec['cli_glue']
    magpie.params.AbstractParamsModel.CLI_BOOLEAN = sec['cli_boolean']
    magpie.params.AbstractParamsModel.CLI_BOOLEAN_PREFIX_TRUE = sec['cli_boolean_prefix_true']
    magpie.params.AbstractParamsModel.CLI_BOOLEAN_PREFIX_FALSE = sec['cli_boolean_prefix_false']
    magpie.params.AbstractParamsModel.SILENT_PREFIX = sec['silent_prefix']
    magpie.params.AbstractParamsModel.SILENT_SUFFIX = sec['silent_suffix']

def setup_xml_model(model, config_section, section):
    for k in [
            'process_pseudo_blocks',
            'process_literals',
            'process_operators',
    ]:
        val = config_section[k]
        if val.lower() in ['true', 't', '1']:
            model.config[k] = True
        elif val.lower() in ['false', 'f', '0']:
            model.config[k] = False
        else:
            raise ValueError('Invalid config file: "{} {}" should be Boolean'.format(section_name, k))
    if (k := 'internodes') in config_section:
        model.config[k] = set(config_section[k].split())
    if 'rename' in config_section:
        h = {}
        for rule in config_section['rename'].split("\n"):
            if rule.strip(): # discard potential initial empty line
                try:
                    k, v = rule.split(':')
                except ValueError:
                    raise ValueError('badly formated rule: "{}"'.format(rule))
                h[k] = set(v.split())
        model.config['tag_rename'] = h
    if 'focus' in config_section:
        model.config['tag_focus'] = set(config_section['focus'].split())

def setup_params_model(model, config_section, section):
    if (k := 'timing') in config_section:
        tmp = config_section[k].split()
        if any((val := timing) not in ['setup', 'compile', 'test', 'run'] for timing in tmp):
            raise ValueError('illegal timing value: {}'.format(val))
        model.config[k] = tmp
    for k in [
            'cli_prefix',
            'cli_glue',
            'cli_boolean',
            'cli_boolean_prefix_true',
            'cli_boolean_prefix_false',
            'silent_prefix',
            'silent_suffix',
    ]:
        if k in config_section:
            model.config[k] = config_section[k]
