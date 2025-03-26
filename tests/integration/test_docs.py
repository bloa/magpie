import pathlib
import re
import subprocess

import pytest

docs_cmds = set()
valid_cmds = [
    r'    (.*python3? .*)',
]
blacklist_cmd = [
    r'local_search',
    r'genetic_improvement',
    r'minisat',
    r'path/to/my/patch',
]
for dotmd in pathlib.Path('docs').glob('**/*.md'):
    with pathlib.Path(dotmd).open('r') as f:
        for line in f:
            for regexp in valid_cmds:
                for cmd in re.findall(regexp, line, re.MULTILINE):
                    if not any(re.search(r, cmd) for r in blacklist_cmd):
                        docs_cmds.add((dotmd, cmd))

@pytest.mark.parametrize(('dotmd', 'cmd'), set(docs_cmds), ids=str)
def test_scenario_algos(dotmd, cmd):
    subprocess.check_call(cmd, shell=True)
