import magpie.algos
import magpie.core
import magpie.fitness
import magpie.models
import magpie.settings
import magpie.utils

def _load_scenario():
    import configparser
    import importlib.resources
    config = configparser.ConfigParser(interpolation=None)
    file_path = importlib.resources.files(__package__).joinpath('scenario_default.txt')
    with file_path.open('r') as f:
        config.read_file(f)
    return {sec: dict(config.items(sec)) for sec in config.sections()}


default_scenario = _load_scenario()
del _load_scenario
