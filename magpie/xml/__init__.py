from .xml_engine import XmlEngine
from .xml_edits import NodeDeletion, NodeReplacement, NodeInsertion, NodeMoving
from .xml_edits import TextSetting, TextWrapping

from .srcml_engine import SrcmlEngine
from .srcml_edits import XmlLineReplacement, XmlLineInsertion, XmlLineDeletion, XmlLineMoving
from .srcml_edits import StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving, StmtSwap
from .srcml_edits import ExprReplacement
from .srcml_edits import ComparisonOperatorSetting, ArithmeticOperatorSetting
from .srcml_edits import NumericSetting, RelativeNumericSetting

# "final" engines only
engines = [
    XmlEngine,
    SrcmlEngine,
]

# "final" edits only
edits = [
    XmlLineReplacement, XmlLineInsertion, XmlLineDeletion, XmlLineMoving,
    StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving, StmtSwap,
    ExprReplacement,
    ComparisonOperatorSetting, ArithmeticOperatorSetting,
    NumericSetting, RelativeNumericSetting,
]
