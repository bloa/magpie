from .xml_model import XmlModel
from .xml_edits import NodeDeletion, NodeReplacement, NodeInsertion, NodeMoving
from .xml_edits import TextSetting, TextWrapping

from .srcml_model import SrcmlModel
from .srcml_edits import XmlLineReplacement, XmlLineInsertion, XmlLineDeletion, XmlLineMoving
from .srcml_edits import StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving, StmtSwap
from .srcml_edits import ExprReplacement
from .srcml_edits import ComparisonOperatorSetting, ArithmeticOperatorSetting
from .srcml_edits import NumericSetting, RelativeNumericSetting

# "final" models only
known_models = [
    XmlModel,
    SrcmlModel,
]

# "final" edits only
known_edits = [
    XmlLineReplacement, XmlLineInsertion, XmlLineDeletion, XmlLineMoving,
    StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving, StmtSwap,
    ExprReplacement,
    ComparisonOperatorSetting, ArithmeticOperatorSetting,
    NumericSetting, RelativeNumericSetting,
]
