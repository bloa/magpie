import re

from .abstract_engine import AbstractParamsEngine
from .realms import Realm

class ConfigFileParamsEngine(AbstractParamsEngine):
    @classmethod
    def get_contents(cls, file_path):
        with open(file_path) as config_file:
            for line in config_file.readlines():
                # ignore comments and empty lines
                if re.match(r"^\s*(#.*)?$", line):
                    continue

                # special setup options
                m = re.match(r"^CLI_PREFIX\s*=\s*\"([^\"]*)\"", line)
                if m:
                    cls.CLI_PREFIX = m.group(1)
                    continue
                m = re.match(r"^CLI_GLUE\s*=\s*\"([^\"]*)\"", line)
                if m:
                    cls.CLI_GLUE = m.group(1)
                    continue
                m = re.match(r"^CLI_BOOLEAN\s*=\s*\"([^\"]*)\"", line)
                if m:
                    cls.CLI_BOOLEAN = m.group(1)
                    continue
                m = re.match(r"^CLI_BOOLEAN_PREFIX_TRUE\s*=\s*\"([^\"]*)\"", line)
                if m:
                    cls.CLI_BOOLEAN_PREFIX_TRUE = m.group(1)
                    continue
                m = re.match(r"^CLI_BOOLEAN_PREFIX_FALSE\s*=\s*\"([^\"]*)\"", line)
                if m:
                    cls.CLI_BOOLEAN_PREFIX_FALSE = m.group(1)
                    continue

                # categorical parameters
                m = re.match(r"^\s*(\S+)\s*\{([^}]+)\}\s*\[([^\]]+)\]", line)
                if m:
                    param = m.group(1)
                    default = m.group(3)
                    values = [s.strip() for s in m.group(2).split(',')]
                    if default not in values:
                        raise RuntimeError('Illegal default value for {}: "{}"'.format(param, default))
                    cls.PARAMS[param] = [default, Realm.categorical(values)]
                    continue

                # continuous parameters
                m = re.match(r"^\s*(\S+)\s*\(([^,]+),([^,]+)\)\s*\[([^\]]+)\]", line)
                if m:
                    param = m.group(1)
                    default = float(m.group(4).strip())
                    values = [float(x.strip()) for x in [m.group(2), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise RuntimeError('Illegal default value for {}: "{}"'.format(param, default))
                    cls.PARAMS[param] = [default, Realm.uniform(*values)]
                    continue
                m = re.match(r"^\s*(\S+)\s*e\(([^,]+),([^,]+)\)\s*\[([^\]]+)\]", line)
                if m:
                    param = m.group(1)
                    default = float(m.group(4).strip())
                    values = [float(x.strip()) for x in [m.group(2), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise RuntimeError('Illegal default value for {}: "{}"'.format(param, default))
                    cls.PARAMS[param] = [default, Realm.exponential(*values)]
                    continue
                m = re.match(r"^\s*(\S+)\s*e\(([^,]+),([^,]+),([^,]+)\)\s*\[([^\]]+)\]", line)
                if m:
                    param = m.group(1)
                    default = float(m.group(5).strip())
                    values = [float(x.strip()) for x in [m.group(2), m.group(3), m.group(4)]]
                    if default > values[1] or default < values[0]:
                        raise RuntimeError('Illegal default value for {}: "{}"'.format(param, default))
                    cls.PARAMS[param] = [default, Realm.exponential(*values)]
                    continue

                # integer parameters
                m = re.match(r"^\s*(\S+)\s*\[([^,]+),([^,]+)\]\s*\[([^\]]+)\]", line)
                if m:
                    param = m.group(1)
                    default = int(m.group(4).strip())
                    values = [int(x.strip()) for x in [m.group(2), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise RuntimeError('Illegal default value for {}: "{}"'.format(param, default))
                    cls.PARAMS[param] = [default, Realm.uniform_int(*values)]
                    continue
                m = re.match(r"^\s*(\S+)\s*g\[([^,]+),([^,]+)\]\s*\[([^\]]+)\]", line)
                if m:
                    param = m.group(1)
                    default = int(m.group(4).strip())
                    values = [int(x.strip()) for x in [m.group(2), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise RuntimeError('Illegal default value for {}: "{}"'.format(param, default))
                    cls.PARAMS[param] = [default, Realm.geometric(*values)]
                    continue
                m = re.match(r"^\s*(\S+)\s*g\[([^,]+),([^,]+),([^,]+)\]\s*\[([^\]]+)\]", line)
                if m:
                    param = m.group(1)
                    default = int(m.group(5).strip())
                    values = [int(x.strip()) for x in [m.group(2), m.group(3), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise RuntimeError('Illegal default value for {}: "{}"'.format(param, default))
                    cls.PARAMS[param] = [default, Realm.geometric(*values)]
                    continue

                # forbidden parameters
                m = re.match(r"^{([^=}]+=[^=}]+(?:,[^=}]+=[^=}]+)*)\}", line)
                if m:
                    tmp = {}
                    for s in m.group(1).split(','):
                        s1, s2 = s.split('=')
                        if s1 not in cls.PARAMS.keys():
                            raise RuntimeError('Illegal forbidden parameter: "{}"'.format(s1.strip()))
                        tmp[s1.strip()] = s2.strip()
                    cls.FORB.append(tmp)
                    continue

                # conditional parameters (multiple values)
                m = re.match(r"^\s*([^|]+)\s*\|\s*([^{]+?)\s* in \{(\S*)\}", line)
                if m:
                    tmp = [m.group(1).strip(), m.group(2).strip(), [s.strip() for s in m.group(2).strip().split(',')]]
                    if tmp[0] not in cls.PARAMS.keys():
                        raise RuntimeError('Illegal conditional parameter: "{}"'.format(tmp[0]))
                    if tmp[1] not in cls.PARAMS.keys():
                        raise RuntimeError('Illegal conditional parameter: "{}"'.format(tmp[1]))
                    cls.CONDS.append(tmp)
                    continue

                # conditional parameters (single values)
                m = re.match(r"^\s*([^|]+)\s*\|\s*([^{]+?)\s*==\s*(\S*)", line)
                if m:
                    tmp = [m.group(1).strip(), m.group(2).strip(), [m.group(2).strip()]]
                    if tmp[0] not in cls.PARAMS.keys():
                        raise RuntimeError('Illegal conditional parameter: "{}"'.format(tmp[0]))
                    if tmp[1] not in cls.PARAMS.keys():
                        raise RuntimeError('Illegal conditional parameter: "{}"'.format(tmp[1]))
                    cls.CONDS.append(tmp)
                    continue
                raise RuntimeError('Unable to parse line: "{}"'.format(line.strip()))
        cls.KEYS = [k for k in cls.PARAMS.keys()]
        return cls.get_default_params()

    @classmethod
    def would_be_ignored(cls, config, key, value):
        return super().would_be_ignored(config, key, str(value))

    @classmethod
    def would_be_valid(cls, config, key, value):
        return super().would_be_valid(config, key, str(value))
