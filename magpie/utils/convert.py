import re

from .known import algos as known_algos
from .known import edits as known_edits
from .known import fitness as known_fitness
from .known import models as known_models
from .known import software as known_software


def model_from_string(s):
    for klass in known_models:
        if klass.__name__ == s:
            return klass
    msg = f'Unknown model class "{s}"'
    raise RuntimeError(msg)

def edit_from_string(s):
    s2 = s.lower().replace('_', '') + 'edit'
    for klass in known_edits:
        if klass.__name__.lower() == s2:
            return klass
    m = re.search(r'(<.+>)', s)
    if m:
        klass = edit_from_string(s.replace(m.group(1), 'Templated'))
        return klass.template(m.group(1))
    msg = f'Unknown edit class "{s}Edit"'
    raise RuntimeError(msg)

def fitness_from_string(s):
    s2 = s.lower().replace('_', '') + 'fitness'
    for klass in known_fitness:
        if klass.__name__.lower() == s2:
            return klass
    m = re.search(r'(<.+>)', s)
    if m:
        klass = fitness_from_string(s.replace(m.group(1), 'Templated'))
        return klass.template(m.group(1))
    msg = f'Unknown fitness class "{s}Fitness"'
    raise RuntimeError(msg)

def software_from_string(s):
    for klass in known_software:
        if klass.__name__ == s:
            return klass
    msg = f'Unknown software class "{s}"'
    raise RuntimeError(msg)

def algo_from_string(s):
    for klass in known_algos:
        if klass.__name__ == s:
            return klass
    msg = f'Unknown algorithm class "{s}"'
    raise RuntimeError(msg)


def str_to_int_or_none(s):
    return None if s.strip().lower() in ['', 'none'] else int(float(s))

def str_to_float_or_none(s):
    return None if s.strip().lower() in ['', 'none'] else float(s)

def str_to_str_or_none(s):
    return None if s.strip().lower() in ['', 'none'] else s.strip()

def str_to_bool(s):
    match s.strip().lower():
        case 'true' | 't' | '1':
            return True
        case 'false' | 'f' | '0':
            return False
        case _:
            raise ValueError
