from .edit import Edit
from .patch import Patch
from .execresult import ExecResult
from .runresult import RunResult

from .abstract_model import AbstractModel
from .abstract_software import AbstractSoftware
from .abstract_algorithm import AbstractAlgorithm

from .basic_software import BasicSoftware
from .basic_algorithm import BasicAlgorithm
from .basic_protocol import BasicProtocol

from .scenario import default_scenario
from .setup import pre_setup, setup

# "final" software only
known_software = [
    BasicSoftware,
]

# "final" protocols only
known_protocols = [
    BasicProtocol,
]
