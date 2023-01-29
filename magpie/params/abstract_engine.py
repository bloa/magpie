from abc import abstractmethod
import random

from ..base import AbstractEngine
from .realms import Realm

class AbstractParamsEngine(AbstractEngine):
    PARAMS = {}
    CONDS = []
    FORB = []
    KEYS = []

    CLI_PREFIX = "--"
    CLI_GLUE = "="
    CLI_BOOLEAN = 'show' # show ; hide ; prefix
    CLI_BOOLEAN_PREFIX_TRUE = ''
    CLI_BOOLEAN_PREFIX_FALSE = 'no-'

    @classmethod
    def get_contents(cls, file_path):
        return cls.get_default_params()

    @classmethod
    def get_locations(cls, contents_of_file):
        return {'param': cls.KEYS}

    @classmethod
    def get_default_params(cls):
        return {k: cls.PARAMS[k][0] for k in cls.KEYS}

    @classmethod
    def get_source(cls, program, file_name, index):
        pass

    @classmethod
    def write_to_tmp_dir(cls, contents_of_file, tmp_path):
        pass

    @classmethod
    def location_names(cls, file_locations, target_file, target_type):
        return file_locations[target_file][target_type]

    @classmethod
    def dump(cls, contents_of_file):
        return "\n".join(['{} := {}'.format(k, repr(v)) for k,v in contents_of_file.items() if not cls.would_be_ignored(contents_of_file, k, v)])

    @classmethod
    def show_location(cls, file_contents, file_locations, target_file, target_type, target_loc):
        if target_type != 'param':
            return '(unsupported)'
        return '{}: {} default={}'.format(target_loc, str(cls.PARAMS[target_loc][1]), repr(cls.PARAMS[target_loc][0]))

    @classmethod
    def random_target(cls, locations, weights, target_file, target_type=None):
        if target_type is None:
            target_type = random.choice(locations[target_file])
        if weights and target_file in weights and target_type in weights[target_file]:
            total_weight = sum(weights[target_file][target_type].values())
            r = random.uniform(0, total_weight)
            for loc, w in weights[target_file][target_type].items():
                if r < w:
                    return (target_file, target_type, loc)
                r -= w
            return None
        else:
            try:
                loc = random.choice(locations[target_file][target_type])
                return (target_file, target_type, loc)
            except (KeyError, ValueError):
                return None

    @classmethod
    def resolve_cli(cls, params):
        return ' '.join([s for s in [cls.resolve_cli_param(params, k, v) for k,v in params.items() if not cls.would_be_ignored(params, k, v)] if s != ''])

    @classmethod
    def resolve_cli_param(cls, all_params, param, value):
        if str(value) == 'True':
            if cls.CLI_BOOLEAN == 'hide':
                return '{}{}'.format(cls.CLI_PREFIX, param)
            elif cls.CLI_BOOLEAN == 'prefix':
                return '{}{}{}'.format(cls.CLI_PREFIX, cls.CLI_BOOLEAN_PREFIX_TRUE, param)
        elif str(value) == 'False':
            if cls.CLI_BOOLEAN == 'hide':
                return ''
            elif cls.CLI_BOOLEAN == 'prefix':
                return '{}{}{}'.format(cls.CLI_PREFIX, cls.CLI_BOOLEAN_PREFIX_FALSE, param)
        return '{}{}{}{}'.format(cls.CLI_PREFIX, param, cls.CLI_GLUE, repr(value))

    @classmethod
    def would_be_ignored(cls, config, key, value):
        return any(config[_k2] not in _vals for (_k1, _k2, _vals) in cls.CONDS if _k1 == key)

    @classmethod
    def would_be_valid(cls, config, key, value):
        for d in cls.FORB:
            forb = True
            for k in d.keys():
                if (k != key and d[k] != config[k]) or (k == key and d[k] != value):
                    forb = False
                    break
            if forb:
                return False
        return True

    @classmethod
    def do_set(cls, contents, locations, new_contents, new_locations, target, value):
        config = new_contents[target[0]]
        key = target[1]
        used = cls.would_be_valid(config, key, value) and not cls.would_be_ignored(config, key, value)
        if used:
            config[key] = value
        return used

    @classmethod
    def random_value(cls, param_key):
        realm = cls.PARAMS[param_key][1]
        return Realm.random_value_from_realm(realm)
