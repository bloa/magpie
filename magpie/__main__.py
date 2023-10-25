#!/usr/bin/env python3

import os
import pathlib
import runpy
import sys

root = pathlib.Path('.')
all_valid_targets = sum([sorted(root.glob(f'magpie/{d}/*.py')) for d in ['bin', 'utils']], [])

def usage():
    print('usage: python3 magpie ((magpie/){bin,utils}/)TARGET(.py) [ARGS]...')
    print('possible TARGET:', file=sys.stderr)
    for path in all_valid_targets:
        print(f'    {path.stem:16}	({path})', file=sys.stderr)

def get_valid_target(argv):
    if len(argv) < 2:
        return None
    path = pathlib.PurePath(argv[1])
    for target in all_valid_targets:
        if path.stem == target.stem:
            return f'magpie.{target.parent.name}.{path.stem}'
    return None

if __name__ == "__main__":
    target = get_valid_target(sys.argv)
    if not target:
        usage()
        exit(1)

    # replace current process
    sys.argv = sys.argv[1:]
    sys.path.append('.')
    runpy.run_module(target, run_name='__main__', alter_sys=True)
