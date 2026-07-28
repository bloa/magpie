import pathlib
import re

import magpie.settings
from magpie.parsing import MathTree

from .abstract_software import AbstractSoftware
from .errors import ScenarioError


class BasicSoftware(AbstractSoftware):
    def __init__(self, config):
        self.config = config
        self.logger = None
        self.path = None
        self.basename = None
        self.target_files = []
        self.ingredient_files = []
        self.model_rules = None
        self.model_config = None
        self.fitness_trees = None
        self.noop_variant = None

    def setup(self):
        sec = self.config['software']
        self.path = pathlib.Path(sec['path'].strip()).resolve()
        self.basename = self.path.name
        self.target_files = sec['target_files'].split()
        self.ingredient_files = sec['ingredient_files'].split()

        # model rules
        self.model_rules = self._setup_model_rules(sec['model_rules'])
        if not self.model_rules:
            msg = 'Invalid config file: empty "[software] model_rules"'
            raise ScenarioError(msg)

        # model config
        self.model_config = self._setup_model_config(sec['model_config'])
        if not self.model_config:
            msg = 'Invalid config file: empty "[software] model_config"'
            raise ScenarioError(msg)

        # fitness type
        self.fitness_trees = self._setup_model_fitness(sec['fitness'])
        if not self.fitness_trees:
            msg = 'Invalid config file: empty "[software] fitness"'
            raise ScenarioError(msg)
        self.fitness_objectives = {s: magpie.utils.fitness_from_string(s)(self) for tree in self.fitness_trees for s in tree.variables}

        # init
        self.init_performed = False
        self.init_cmd = magpie.utils.str_to_str_or_none(sec['init_cmd'])
        self.init_timeout = magpie.utils.str_to_float_or_none(sec['init_timeout'])
        self.init_lengthout = magpie.utils.str_to_int_or_none(sec['init_lengthout'])

        # setup
        self.setup_performed = False
        self.setup_cmd = magpie.utils.str_to_str_or_none(sec['setup_cmd'])
        self.setup_timeout = magpie.utils.str_to_float_or_none(sec['setup_timeout'])
        self.setup_lengthout = magpie.utils.str_to_int_or_none(sec['setup_lengthout'])

        # compile
        self.compile_cmd = magpie.utils.str_to_str_or_none(sec['compile_cmd'])
        self.compile_timeout = magpie.utils.str_to_float_or_none(sec['compile_timeout'])
        self.compile_lengthout = magpie.utils.str_to_int_or_none(sec['compile_lengthout'])

        # test
        self.test_cmd = magpie.utils.str_to_str_or_none(sec['test_cmd'])
        self.test_timeout = magpie.utils.str_to_float_or_none(sec['test_timeout'])
        self.test_lengthout = magpie.utils.str_to_int_or_none(sec['test_lengthout'])

        # run
        self.run_cmd = magpie.utils.str_to_str_or_none(sec['run_cmd'])
        self.run_timeout = magpie.utils.str_to_float_or_none(sec['run_timeout'])
        self.run_lengthout = magpie.utils.str_to_int_or_none(sec['run_lengthout'])

        # batch parameters
        self.batch_fitness_strategy = sec['batch_fitness_strategy']
        known_strategies = ['sum', 'average', 'median']
        if self.batch_fitness_strategy not in known_strategies:
            tmp = '/'.join(known_strategies)
            msg = f'Invalid config file: "[software] batch_fitness_strategy" key must be {tmp}'
            raise ScenarioError(msg)
        self.batch_bin_fitness_strategy = sec['batch_fitness_strategy']
        known_strategies = ['aggregate', 'sum', 'average', 'median', 'q10', 'q25', 'q75', 'q90']
        if self.batch_fitness_strategy not in known_strategies:
            tmp = '/'.join(known_strategies)
            msg = f'Invalid config file: "[software] batch_bin_fitness_strategy" key must be {tmp}'
            raise ScenarioError(msg)
        self.batch_timeout = magpie.utils.str_to_float_or_none(sec['batch_timeout'])
        self.batch_lengthout = magpie.utils.str_to_int_or_none(sec['batch_lengthout'])

    @staticmethod
    def _setup_model_rules(value):
        rules = []
        try:
            for rule in value.split('\n'):
                if rule: # discard potential initial empty line
                    k, v = rule.split(':')
                    v = v.strip()
                    if re.search(r'[^_A-z0-9]', v):
                        msg = f'Badly formated rule: "{rule}"'
                        raise ScenarioError(msg)
                    rules.append((k.strip(), v))
        except ValueError as e:
            msg = f'Badly formated rule: "{rule}"'
            raise ScenarioError(msg) from e
        return rules

    @staticmethod
    def _setup_model_config(value):
        config = []
        try:
            for rule in value.split('\n'):
                if rule: # discard potential initial empty line
                    k, v = rule.split(':')
                    v = v.strip()
                    if re.search(r'[^_A-z0-9]', v[1:-1]) or v[0]+v[-1] != '[]':
                        msg = f'Badly formated rule: "{rule}"'
                        raise ScenarioError(msg)
                    config.append((k.strip(), v[1:-1]))
        except ValueError as e:
            msg = f'Badly formated rule: "{rule}"'
            raise ScenarioError(msg) from e
        return config

    @staticmethod
    def _setup_model_fitness(expr):
        # multi-objective fitness
        if ';' in expr:
            tmp = [BasicSoftware._setup_model_fitness(s) for s in expr.split(';')]
            return [tree for trees in tmp for tree in trees]
        if '\n' in expr:
            tmp = [BasicSoftware._setup_model_fitness(s) for s in expr.split()]
            return [tree for trees in tmp for tree in trees]
        # replace variable names
        var_map = {}
        var_count = 1
        pattern = re.compile(r'\b[a-zA-Z_]\w*(?:<[^<>]*?>)?')
        def replacer(_match):
            nonlocal var_count
            original = _match.group(0)
            if original not in var_map:
                var_map[original] = f'var{var_count}'
                var_count += 1
            return var_map[original]
        new_expr = pattern.sub(replacer, expr)
        # parse expression
        try:
            tree = MathTree.from_string(new_expr)
        except SyntaxError as e:
            msg = 'Invalid config file: unable to parse "[software] fitness"'
            raise ScenarioError(msg) from e
        except TypeError as e:
            msg = 'Invalid config file: "[software] fitness" only supports numeric expressions'
            raise ScenarioError(msg) from e
        # put original variable names back
        for (old, new) in var_map.items():
            tree.rename(new, old)
        return [tree]

magpie.utils.known_software.append(BasicSoftware)
