#!/usr/bin/env python3

import glob
import os
import pathlib
import sys

def usage(pref, suff):
    print('usage: {} TARGET [ARGS]...'.format(sys.argv[0]))
    print('possible targets:', file=sys.stderr)
    for f in sorted(glob.glob('bin/*.py')):
        path = pathlib.PurePath('bin' if pref else '') / '{}{}'.format(f[4:-3], '.py' if suff else '')
        print('    {}'.format(path), file=sys.stderr)
    exit(1)

# split argv
if len(sys.argv) == 1:
    usage(None, None)
path = pathlib.PurePath(sys.argv[1])
argv = sys.argv[2:]

# split target "path"
pref = str(path.parent) if str(path.parent) != '.' else None
stem = path.stem
suff = ''.join(path.suffixes) if path.suffix else None

# check usage
if ((pref and pref != 'bin') or
    (suff and suff != '.py') or
    not (pathlib.Path('bin') / '{}.py'.format(stem)).exists()):
    usage(pref, suff)

# replace current process
os.execlp('python3', 'python3', '-m', 'bin.{}'.format(stem), *argv)
