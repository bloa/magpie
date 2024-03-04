from .known import algos as known_algos
from .known import edits as known_edits
from .known import models as known_models
from .known import protocols as known_protocols
from .known import software as known_software


def model_from_string(s):
    for klass in known_models:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown model class "{s}"')

def edit_from_string(s):
    for klass in known_edits:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown edit class "{s}"')

def protocol_from_string(s):
    for klass in known_protocols:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown protocol class "{s}"')

def software_from_string(s):
    for klass in known_software:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown software class "{s}"')

def algo_from_string(s):
    for klass in known_algos:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown algorithm class "{s}"')
