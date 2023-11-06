from .xml_model import XmlModel
from .xml_edits import XmlNodeDeletion, XmlNodeReplacement, XmlNodeInsertion
from .xml_edits import XmlTextSetting, XmlTextWrapping

from .srcml_model import SrcmlModel
from .srcml_edits import XmlLineDeletion, XmlLineReplacement, XmlLineInsertion
from .srcml_edits import SrcmlStmtDeletion, SrcmlStmtReplacement, SrcmlStmtInsertion
from .srcml_edits import SrcmlExprReplacement
from .srcml_edits import SrcmlComparisonOperatorSetting, SrcmlArithmeticOperatorSetting
from .srcml_edits import SrcmlNumericSetting, SrcmlRelativeNumericSetting

# "final" models only
known_models = [
    XmlModel,
    SrcmlModel,
]

# "final" edits only
known_edits = [
    XmlLineDeletion, XmlLineReplacement, XmlLineInsertion,
    SrcmlStmtDeletion, SrcmlStmtReplacement, SrcmlStmtInsertion,
    SrcmlExprReplacement,
    SrcmlComparisonOperatorSetting, SrcmlArithmeticOperatorSetting,
    SrcmlNumericSetting, SrcmlRelativeNumericSetting,
]
