from magpie.core import AbstractModel
from .realms import Realm

class AbstractParamsModel(AbstractModel):
    TIMING = ['run']
    CLI_PREFIX = "--"
    CLI_GLUE = "="
    CLI_BOOLEAN = 'show' # show ; hide ; prefix
    CLI_BOOLEAN_PREFIX_TRUE = ''
    CLI_BOOLEAN_PREFIX_FALSE = 'no-'
    CLI_NONE = 'hide' # show ; hide
    SILENT_PREFIX = '@'
    SILENT_SUFFIX = '$'

    def __init__(self, filename):
        super().__init__(filename)
        self.indirect_locations = False
        self.config = {
            'timing': self.TIMING,
            'cli_prefix': self.CLI_PREFIX,
            'cli_glue': self.CLI_GLUE,
            'cli_boolean': self.CLI_BOOLEAN,
            'cli_boolean_prefix_true': self.CLI_BOOLEAN_PREFIX_TRUE,
            'cli_boolean_prefix_false': self.CLI_BOOLEAN_PREFIX_FALSE,
            'cli_none': self.CLI_NONE,
            'silent_prefix': self.SILENT_PREFIX,
            'silent_suffix': self.SILENT_SUFFIX,
        }

    def dump(self):
        return ''.join([f'{k} := {repr(v)}\n' for k,v in self.contents['current'].items() if not self.would_be_ignored(k, v)])

    def show_location(self, target_type, target_loc):
        if target_type != 'param':
            return '(unsupported)'
        space = self.contents['space'][target_loc]
        default = self.contents['current'][target_loc]
        return f'{target_loc}: {space} default={default}'

    def random_value(self, key):
        realm = self.contents['space'][key]
        return Realm.random_value_from_realm(realm)

    def resolve_cli(self):
        all_params = self.contents['current']
        tmp = [self.resolve_cli_param(k, v) for k,v in all_params.items() if not self.would_be_ignored(k, v)]
        return ' '.join([s for s in tmp if s != ''])

    def resolve_cli_param(self, param, value):
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
        return f'{prefix}{cli_param}{glue}{repr(value)}'

    def would_be_ignored(self, key, value):
        return any(self.contents['current'][_k2] not in _vals for (_k1, _k2, _vals) in self.contents['conditionals'] if _k1 == key)

    def would_be_valid(self, key, value):
        for d in self.contents['forbidden']:
            forbidden = True
            for k in d.keys():
                if (k != key and d[k] != self.contents['current'][k]) or (k == key and d[k] != value):
                    forbidden = False
                    break
            if forbidden:
                return False
        return True

    def do_set(self, target, value):
        key = target[2]
        used = self.would_be_valid(key, value) and not self.would_be_ignored(key, value)
        if used:
            self.contents['current'][key] = value
        return used
