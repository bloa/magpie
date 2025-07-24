import pathlib
import re

import pytest

import magpie

scenario_files = set()
blacklist = [
    r'minisat',
    r'quixbugs',
]
for txt in pathlib.Path('examples').glob('**/scenario*.txt'):
    print(txt)
    if not any(re.search(r, str(txt)) for r in blacklist):
        scenario_files.add(txt)

@pytest.mark.parametrize('filename', scenario_files, ids=str)
def test_scenario_commands(filename):
    protocol = magpie.core.SearchProtocol(filename)
    protocol.config['search']['algorithm'] = 'DummySearch'
    protocol.config['search']['warmup'] = '0'
    protocol.setup()
    protocol.run()
