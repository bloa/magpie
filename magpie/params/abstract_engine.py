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
    def dump(cls, contents_of_file):
        return "\n".join(['{} := {}'.format(k, repr(v)) for k,v in contents_of_file.items() if not cls.would_be_ignored(contents_of_file, k, v)])

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
        key = cls.KEYS[target[1]]
        used = cls.would_be_valid(config, key, value) and not cls.would_be_ignored(config, key, value)
        if used:
            config[key] = value
        return used

    @classmethod
    def random_value(cls, param_id):
        realm = cls.PARAMS[cls.KEYS[param_id]][1]
        return Realm.random_value_from_realm(realm)
