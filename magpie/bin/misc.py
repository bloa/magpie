import ast
import re

import magpie

def algo_from_string(s):
    for klass in magpie.algo.algos:
        if klass.__name__ == s:
            return klass
    raise RuntimeError('Unknown algorithm "{}"'.format(s))

def engine_from_string(s):
    for klass in [*magpie.xml.engines, *magpie.line.engines, *magpie.params.engines]:
        if klass.__name__ == s:
            return klass
    raise RuntimeError('Unknown engine "{}"'.format(s))

def patch_from_string(s):
    patch = magpie.base.Patch()
    for blob in s.split(' | '):
        match = re.search(r"^(\w+)\((.+)\)$", blob)
        for klass in [*magpie.xml.edits, *magpie.line.edits, *magpie.params.edits]:
            if klass.__name__ == match.group(1):
                args = ast.literal_eval("[{}]".format(match.group(2)))
                patch.edits.append(klass(*args))
                break
        else:
            raise RuntimeError('Unknown edit type "{}" in patch'.format(match.group(1)))
    assert str(patch) == s
    return patch

def program_from_string(s):
    for klass in magpie.bin.programs:
        if klass.__name__ == s:
            return klass
    raise RuntimeError('Unknown program "{}"'.format(s))

def protocol_from_string(s):
    for klass in magpie.bin.protocols:
        if klass.__name__ == s:
            return klass
    raise RuntimeError('Unknown protocol "{}"'.format(s))
