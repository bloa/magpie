import ast
import re

import magpie

def algo_from_string(s):
    for klass in magpie.algos.known_algos:
        if klass.__name__ == s:
            return klass
    raise RuntimeError('Unknown algorithm "{}"'.format(s))

def model_from_string(s):
    for klass in magpie.models.known_models:
        if klass.__name__ == s:
            return klass
    raise RuntimeError('Unknown model "{}"'.format(s))

def edit_from_string(s):
    m = re.search(r"^(\w+)\((.+)\)$", s)
    for klass in magpie.models.known_edits:
        if klass.__name__ == m.group(1):
            args = ast.literal_eval("[{}]".format(m.group(2)))
            return klass(*args)
    else:
        raise RuntimeError('Unknown edit type "{}" in patch'.format(m.group(1)))

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
    raise RuntimeError('Unknown software "{}"'.format(s))

def protocol_from_string(s):
    for klass in magpie.core.known_protocols:
        if klass.__name__ == s:
            return klass
    raise RuntimeError('Unknown protocol "{}"'.format(s))
