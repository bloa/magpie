import configparser
import importlib
import pathlib
import random

import magpie.settings

from .errors import ScenarioError
from .abstract_protocol import AbstractProtocol


class BasicProtocol(AbstractProtocol):
    def __init__(self, scenario_file):
        # read scenario file
        config = configparser.ConfigParser()
        config.read_dict(magpie.default_scenario)
        config.read(scenario_file)
        self.config = {sec: dict(config.items(sec)) for sec in config.sections()}

    def setup(self):
        # [magpie] section
        sec = self.config['magpie']
        if val := sec['import']:
            for module in val.split():
                try:
                    s = str(pathlib.Path(self.config['software']['path']) / module)
                    importlib.import_module(s.rstrip('.py').lstrip('./').replace('/', '.'))
                except ModuleNotFoundError:
                    importlib.import_module(val.rstrip('.py').lstrip('./').replace('/', '.'))
        if val := sec['seed']:
            random.seed(int(val))
        else:
            val = random.randint(0, int(1e16))
            random.seed(val)
            sec['seed'] = str(val)

        magpie.settings.log_dir = sec['log_dir']
        magpie.settings.work_dir = sec['work_dir']

        try:
            magpie.settings.local_original_copy = magpie.utils.str_to_bool(sec['local_original_copy'])
        except ValueError as e:
            msg = '[magpie] local_original_copy should be Boolean'
            raise ScenarioError(msg) from e
        magpie.settings.local_original_copy = sec['local_original_name']
        magpie.settings.output_encoding = sec['output_encoding']
        magpie.settings.edit_retries = int(sec['edit_retries'])
        magpie.settings.default_timeout = float(sec['default_timeout'])
        magpie.settings.default_lengthout = int(float(sec['default_lengthout']))
        magpie.settings.diff_method = sec['diff_method']
        try:
            magpie.settings.show_cmd_progress = magpie.utils.str_to_bool(sec['show_cmd_progress'])
        except ValueError as e:
            msg = '[magpie] show_cmd_progress should be Boolean'
            raise ScenarioError(msg) from e
        magpie.settings.cmd_progress_maxlength = int(sec['cmd_progress_maxlength'])
        try:
            magpie.settings.trust_local_filesystem = magpie.utils.str_to_bool(sec['trust_local_filesystem'])
        except ValueError as e:
            msg = '[magpie] trust_local_filesystem should be Boolean'
            raise ScenarioError(msg) from e

        # [magpie.log] section
        sec = self.config['magpie.log']
        try:
            magpie.settings.color_output = magpie.utils.str_to_bool(sec['color_output'])
        except ValueError as e:
            msg = '[magpie.log] color_output should be Boolean'
            raise ScenarioError(msg) from e
        try:
            sec['format_info'].format(counter='', status='', best='', fitness='', ratio='', size='', cached='', log='', patch='', patchifaccept='', patchifbest='', diff='', diffifaccept='', diffifbest='')
        except KeyError as e:
            msg = '[magpie.log] error in format_info format string'
            raise ScenarioError(msg) from e
        magpie.settings.log_format_info = sec['format_info']
        try:
            sec['format_debug'].format(counter='', status='', best='', rawfitness='', fitness='', ratio='', size='', cached='', log='', patch='', patchifaccept='', patchifbest='', diff='', diffifaccept='', diffifbest='')
        except KeyError as e:
            msg = '[magpie.log] error in format_debug format string'
            raise ScenarioError(msg) from e
        magpie.settings.log_format_debug = sec['format_debug']
        try:
            sec['format_fitness'].format(0)
        except KeyError as e:
            msg = '[magpie.log] error in format_fitness format string'
            raise ScenarioError(msg) from e
        magpie.settings.log_format_fitness = sec['format_fitness']
        try:
            sec['format_ratio'].format(0)
        except KeyError as e:
            msg = '[magpie.log] error in format_ratio format string'
            raise ScenarioError(msg) from e
        magpie.settings.log_format_ratio = sec['format_ratio']
        try:
            sec['format_patchif'].format(patch='')
        except KeyError as e:
            msg = '[magpie.log] error in format_patchif format string'
            raise ScenarioError(msg) from e
        magpie.settings.log_format_patchif = sec['format_patchif']
        try:
            sec['format_diffif'].format(diff='')
        except KeyError as e:
            msg = '[magpie.log] error in format_diffif format string'
            raise ScenarioError(msg) from e
        magpie.settings.log_format_diffif = sec['format_diffif']
