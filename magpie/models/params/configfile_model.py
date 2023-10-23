import re

from .abstract_model import AbstractParamsModel
from .realms import Realm

class ConfigFileParamsModel(AbstractParamsModel):
    def get_contents(self, file_path):
        contents = {
            'current': {},
            'space': {},
            'conditionals': [],
            'forbidden': [],
        }

        with open(file_path) as config_file:
            for line in config_file.readlines():
                # ignore comments and empty lines
                if re.match(r"^\s*(#.*)?$", line):
                    continue

                # special setup options
                m = re.match(r"^TIMING\s*=\s*\"([^\"]*)\"(?:\s*#.*)?$", line)
                if m:
                    self.config['timing'] = [s.strip() for s in m.group(1).split()]
                    if any([(witness := s) not in ['setup', 'compile', 'test', 'run'] for s in self.config['timing']]):
                        raise ValueError('Illegal timing value: {}'.format(witness))
                    continue
                m = re.match(r"^CLI_PREFIX\s*=\s*\"([^\"]*)\"(?:\s*#.*)?$", line)
                if m:
                    self.config['cli_prefix'] = m.group(1)
                    continue
                m = re.match(r"^CLI_GLUE\s*=\s*\"([^\"]*)\"(?:\s*#.*)?$", line)
                if m:
                    self.config['cli_glue'] = m.group(1)
                    continue
                m = re.match(r"^CLI_BOOLEAN\s*=\s*\"([^\"]*)\"(?:\s*#.*)?$", line)
                if m:
                    self.config['cli_boolean'] = m.group(1)
                    continue
                m = re.match(r"^CLI_BOOLEAN_PREFIX_TRUE\s*=\s*\"([^\"]*)\"(?:\s*#.*)?$", line)
                if m:
                    self.config['cli_boolean_prefix_true'] = m.group(1)
                    continue
                m = re.match(r"^CLI_BOOLEAN_PREFIX_FALSE\s*=\s*\"([^\"]*)\"(?:\s*#.*)?$", line)
                if m:
                    self.config['cli_boolean_prefix_false'] = m.group(1)
                    continue
                m = re.match(r"^SILENT_PREFIX\s*=\s*\"([^\"]*)\"(?:\s*#.*)?$", line)
                if m:
                    self.config['silent_prefix'] = m.group(1)
                    continue
                m = re.match(r"^SILENT_SUFFIX\s*=\s*\"([^\"]*)\"(?:\s*#.*)?$", line)
                if m:
                    self.config['silent_suffix'] = m.group(1)
                    continue

                # categorical parameters
                m = re.match(r"^\s*(\S+)\s*\{([^}]+)\}\s*\[([^\]]+)\](?:\s*#.*)?$", line)
                if m:
                    param = m.group(1)
                    default = m.group(3)
                    values = [s.strip() for s in m.group(2).split(',')]
                    if default not in values:
                        raise ValueError('Illegal default value for {}: "{}"'.format(param, default))
                    contents['current'][param] = default
                    contents['space'][param] = Realm.categorical(values)
                    continue

                # continuous parameters
                m = re.match(r"^\s*(\S+)\s*\(([^,]+),([^,]+)\)\s*\[([^\]]+)\](?:\s*#.*)?$", line)
                if m:
                    param = m.group(1)
                    default = float(m.group(4).strip())
                    values = [float(x.strip()) for x in [m.group(2), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise ValueError('Illegal default value for {}: "{}"'.format(param, default))
                    contents['current'][param] = default
                    contents['space'][param] = Realm.uniform(*values)
                    continue
                m = re.match(r"^\s*(\S+)\s*e\(([^,]+),([^,]+)\)\s*\[([^\]]+)\](?:\s*#.*)?$", line)
                if m:
                    param = m.group(1)
                    default = float(m.group(4).strip())
                    values = [float(x.strip()) for x in [m.group(2), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise ValueError('Illegal default value for {}: "{}"'.format(param, default))
                    contents['current'][param] = default
                    contents['space'][param] = Realm.exponential(*values)
                    continue
                m = re.match(r"^\s*(\S+)\s*e\(([^,]+),([^,]+),([^,]+)\)\s*\[([^\]]+)\](?:\s*#.*)?$", line)
                if m:
                    param = m.group(1)
                    default = float(m.group(5).strip())
                    values = [float(x.strip()) for x in [m.group(2), m.group(3), m.group(4)]]
                    if default > values[1] or default < values[0]:
                        raise ValueError('Illegal default value for {}: "{}"'.format(param, default))
                    contents['current'][param] = default
                    contents['space'][param] = Realm.exponential(*values)
                    continue

                # integer parameters
                m = re.match(r"^\s*(\S+)\s*\[([^,]+),([^,]+)\]\s*\[([^\]]+)\](?:\s*#.*)?$", line)
                if m:
                    param = m.group(1)
                    default = int(m.group(4).strip())
                    values = [int(x.strip()) for x in [m.group(2), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise ValueError('Illegal default value for {}: "{}"'.format(param, default))
                    contents['current'][param] = default
                    contents['space'][param] = Realm.uniform_int(*values)
                    continue
                m = re.match(r"^\s*(\S+)\s*g\[([^,]+),([^,]+)\]\s*\[([^\]]+)\](?:\s*#.*)?$", line)
                if m:
                    param = m.group(1)
                    default = int(m.group(4).strip())
                    values = [int(x.strip()) for x in [m.group(2), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise ValueError('Illegal default value for {}: "{}"'.format(param, default))
                    contents['current'][param] = default
                    contents['space'][param] = Realm.geometric(*values)
                    continue
                m = re.match(r"^\s*(\S+)\s*g\[([^,]+),([^,]+),([^,]+)\]\s*\[([^\]]+)\](?:\s*#.*)?$", line)
                if m:
                    param = m.group(1)
                    default = int(m.group(5).strip())
                    values = [int(x.strip()) for x in [m.group(2), m.group(3), m.group(3)]]
                    if default > values[1] or default < values[0]:
                        raise ValueError('Illegal default value for {}: "{}"'.format(param, default))
                    contents['current'][param] = default
                    contents['space'][param] = Realm.geometric(*values)
                    continue

                # forbidden parameters
                m = re.match(r"^{([^=}]+==[^=}]+(?:,[^=}]+==[^=}]+)*)\}(?:\s*#.*)?$", line)
                if m:
                    tmp = {}
                    for s in m.group(1).split(','):
                        s1, s2 = s.split('=')
                        if s1 not in contents['current'].keys():
                            raise ValueError('Illegal forbidden parameter: "{}"'.format(s1.strip()))
                        tmp[s1.strip()] = s2.strip()
                    contents['forbidden'].append(tmp)
                    continue

                # conditional parameters (multiple values)
                m = re.match(r"^\s*([^|]+)\s*\|\s*([^{]+?)\s* in \{(\S*)\}(?:\s*#.*)?$", line)
                if m:
                    tmp = [m.group(1).strip(), m.group(2).strip(), [s.strip() for s in m.group(2).strip().split(',')]]
                    if tmp[0] not in contents['current'].keys():
                        raise ValueError('Illegal conditional parameter: "{}"'.format(tmp[0]))
                    if tmp[1] not in contents['current'].keys():
                        raise ValueError('Illegal conditional parameter: "{}"'.format(tmp[1]))
                    contents['conditionals'].append(tmp)
                    continue

                # conditional parameters (single values)
                m = re.match(r"^\s*([^|]+)\s*\|\s*([^{]+?)\s*==\s*(\S*)(?:\s*#.*)?$", line)
                if m:
                    tmp = [m.group(1).strip(), m.group(2).strip(), [m.group(2).strip()]]
                    if tmp[0] not in contents['current'].keys():
                        raise ValueError('Illegal conditional parameter: "{}"'.format(tmp[0]))
                    if tmp[1] not in contents['current'].keys():
                        raise ValueError('Illegal conditional parameter: "{}"'.format(tmp[1]))
                    contents['conditionals'].append(tmp)
                    continue
                raise RuntimeError('Unable to parse line: "{}"'.format(line.strip()))
        return contents

    def would_be_ignored(self, file_contents, key, value):
        return super().would_be_ignored(file_contents, key, str(value))

    def would_be_valid(self, file_contents, key, value):
        return super().would_be_valid(file_contents, key, str(value))
