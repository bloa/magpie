import configparser
import pathlib
import re

import pytest

import magpie

scenario_files = set()
blacklist = [
    r'minisat',
]
for txt in pathlib.Path('examples').glob('**/scenario*.txt'):
    print(txt)
    if not any(re.search(r, str(txt)) for r in blacklist):
        scenario_files.add(txt)

@pytest.fixture
def teardown():
    config = configparser.ConfigParser()
    config.read_dict(magpie.core.default_scenario)
    yield
    magpie.core.pre_setup(config)
    magpie.core.setup(config)

@pytest.mark.parametrize('filename', scenario_files, ids=str)
@pytest.mark.usefixtures('teardown')
def test_scenario_commands(filename):
    # read scenario file
    config = configparser.ConfigParser()
    config.read_dict(magpie.core.default_scenario)
    config.read(filename)
    magpie.core.pre_setup(config)

    # select algorithm
    algo = magpie.algos.DummySearch

    # overwrite search parameters
    config['search']['warmup'] = '0'

    # setup protocol
    magpie.core.setup(config)
    protocol = magpie.utils.protocol_from_string(config['search']['protocol'])()
    protocol.search = algo()
    protocol.software = magpie.utils.software_from_string(config['software']['software'])(config)

    # run experiments
    protocol.run(config)
