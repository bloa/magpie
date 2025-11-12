from .color import color_diff

# get class from string
from .convert import (
    algo_from_string,
    edit_from_string,
    fitness_from_string,
    model_from_string,
    software_from_string,
    str_to_bool,
    str_to_float_or_none,
    str_to_int_or_none,
    str_to_str_or_none,
)

from .display import (
    format_bold,
    format_diff,
    format_header,
    format_subheader,
)

from .fitness import (
    dominates,
    dominates_or_equal,
    pareto,
)

# "final" classes only
from .known import algos as known_algos
from .known import edits as known_edits
from .known import models as known_models
from .known import protocols as known_protocols
from .known import software as known_software
