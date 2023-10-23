from .algorithm import BasicAlgorithm
from .software import BasicSoftware
from .protocol import BasicProtocol
from .config import default_config
from .setup import pre_setup, setup, setup_xml_model, setup_params_model
from .misc import algo_from_string, model_from_string, patch_from_string, software_from_string, protocol_from_string

# "final" softwares only
softwares = [
    BasicSoftware,
]

# "final" protocols only
protocols = [
    BasicProtocol,
]
