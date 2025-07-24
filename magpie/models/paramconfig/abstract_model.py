import magpie.core

from .realms import Realm


class AbstractConfigModel(magpie.core.AbstractModel):
    def __init__(self, filename, software):
        super().__init__(filename, software)
        self.indirect_locations = False
        config = software.config['paramconfig'].copy()
        if sec := self._resolve_config_section(software, filename):
            config.update(software.config[sec])
        if (k := 'timing') in config:
            tmp = config[k].split()
            if any((val := timing) not in ['setup', 'compile', 'test', 'run'] for timing in tmp):
                msg = f'Illegal timing value: [paramconfig] "{val}"'
                raise magpie.core.ScenarioError(msg)
            self.config[k] = tmp
        for k in [
                'cli_prefix',
                'cli_glue',
                'cli_boolean',
                'cli_boolean_prefix_true',
                'cli_boolean_prefix_false',
                'cli_none',
                'silent_prefix',
                'silent_suffix',
        ]:
            if k in config:
                self.config[k] = config[k]

    def resolve_dynamic_parameters(self, current):
        all_params = current.copy()
        for (key, tree1, tree2) in self.contents['dynamic']:
            if tree2 is None or tree2.evaluate(all_params):
                all_params[key] = tree1.evaluate(all_params)
        return all_params

    def dump(self):
        all_params = self.resolve_dynamic_parameters(self.contents['current'])
        return ''.join([f'{k} := {v!r}\n' for k,v in all_params.items() if not self.would_be_ignored(k, all_params)])

    def show_location(self, target_type, target_loc):
        if target_type != 'param':
            raise ValueError
        tag_start = ''
        tag_end = ':'
        default_start = 'default='
        if magpie.settings.color_output:
            tag_start = f'\033[36m{tag_start}'
            tag_end = f'{tag_end}\033[0m'
            default_start = f'\033[30m{default_start}\033[0m'
        space = self.contents['space'][target_loc]
        default = self.contents['current'][target_loc]
        return f'{tag_start}{target_loc}{tag_end} {space} {default_start}{default}'

    def random_value(self, key):
        realm = self.contents['space'][key]
        return Realm.random_value_from_realm(realm)

    def update_cli(self, variant, cli, step):
        if step in self.config['timing']:
            all_params = self.contents['current']
            return f'{cli} {self.build_resolved_cli(all_params)}'
        return cli

    def build_resolved_cli(self, all_params):
        return self.build_raw_cli(self.resolve_dynamic_parameters(all_params))

    def build_raw_cli(self, all_params):
        tmp = [self.format_cli_param(k, v) for k,v in all_params.items() if not self.would_be_ignored(k, all_params)]
        return ' '.join([s for s in tmp if s != ''])

    def format_cli_param(self, param, value):
        if param.startswith(self.config['silent_prefix']):
            return ''
        prefix = self.config['cli_prefix']
        if self.config['silent_suffix'] in param:
            cli_param, *_ = param.split(self.config['silent_suffix'])
        else:
            cli_param = param
        if str(value) == 'True':
            if self.config['cli_boolean'] == 'hide':
                return f'{prefix}{cli_param}'
            if self.config['cli_boolean'] == 'prefix':
                bool_prefix = self.config['cli_boolean_prefix_true']
                return f'{prefix}{bool_prefix}{cli_param}'
        elif str(value) == 'False':
            if self.config['cli_boolean'] == 'hide':
                return ''
            if self.config['cli_boolean'] == 'prefix':
                bool_prefix = self.config['cli_boolean_prefix_false']
                return f'{prefix}{bool_prefix}{cli_param}'
        elif str(value) == 'None':
            if self.config['cli_none'] == 'hide':
                return ''
        glue = self.config['cli_glue']
        return f'{prefix}{cli_param}{glue}{value!r}'

    def would_be_ignored(self, key, all_params):
        trees = [tree for (_key, tree) in self.contents['conditionals'] if _key == key]
        return bool(trees) and not any(tree.evaluate(all_params) for tree in trees)

    def would_be_valid(self, all_params):
        return all(tree.evaluate(all_params) for tree in self.contents['asserts'])

    def do_set(self, target, value):
        key = target[2]
        all_params = self.contents['current'].copy()
        if all_params[key] == value:
            return False
        old_cli = self.build_resolved_cli(all_params)
        all_params[key] = value
        all_params = self.resolve_dynamic_parameters(all_params)
        if not self.would_be_valid(all_params) or self.build_raw_cli(all_params) == old_cli:
            return False
        self.contents['current'][key] = value
        return True
