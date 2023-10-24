from . import astor
from . import line
from . import params
from . import xml

# "final" models only
known_models = [
    *astor.known_models,
    *line.known_models,
    *params.known_models,
    *xml.known_models,
]

# "final" edits only
known_edits = [
    *astor.known_edits,
    *line.known_edits,
    *params.known_edits,
    *xml.known_edits,
]
