import ast
import re

import magpie.core
import magpie.algos
import magpie.models

def algo_from_string(s):
    for klass in magpie.algos.known_algos:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown algorithm "{s}"')

def model_from_string(s):
    for klass in magpie.models.known_models:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown model "{s}"')

def edit_from_string(s):
    m = re.search(r"^(\w+)\((.+)\)$", s)
    for klass in magpie.models.known_edits:
        if klass.__name__ == m.group(1):
            args = ast.literal_eval(f'[{m.group(2)}]')
            return klass(*args)
    raise RuntimeError(f'Unknown edit type "{m.group(1)}" in patch')

def patch_from_string(s):
    patch = magpie.core.Patch()
    if s == "":
        return patch
    for blob in s.split(' | '):
        patch.edits.append(edit_from_string(blob))
    assert str(patch) == s
    return patch

def software_from_string(s):
    for klass in magpie.core.known_software:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown software "{s}"')

def protocol_from_string(s):
    for klass in magpie.core.known_protocols:
        if klass.__name__ == s:
            return klass
    raise RuntimeError(f'Unknown protocol "{s}"')
