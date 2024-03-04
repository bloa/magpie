import magpie.utils

from .xml_edits import AbstractXmlNodeDeletion, AbstractXmlNodeReplacement, AbstractXmlNodeInsertion
from .xml_edits import AbstractXmlTextSetting, AbstractXmlTextWrapping

class XmlLineDeletion(AbstractXmlNodeDeletion):
    NODE_TAG = 'line'

magpie.utils.known_edits.append(XmlLineDeletion)

class XmlLineReplacement(AbstractXmlNodeReplacement):
    NODE_TAG = 'line'

magpie.utils.known_edits.append(XmlLineReplacement)

class XmlLineInsertion(AbstractXmlNodeInsertion):
    NODE_PARENT_TAG = 'unit'
    NODE_TAG = 'line'

magpie.utils.known_edits.append(XmlLineInsertion)

class SrcmlStmtDeletion(AbstractXmlNodeDeletion):
    NODE_TAG = 'stmt'

magpie.utils.known_edits.append(SrcmlStmtDeletion)

class SrcmlStmtReplacement(AbstractXmlNodeReplacement):
    NODE_TAG = 'stmt'

magpie.utils.known_edits.append(SrcmlStmtReplacement)

class SrcmlStmtInsertion(AbstractXmlNodeInsertion):
    NODE_PARENT_TAG = 'block'
    NODE_TAG = 'stmt'

magpie.utils.known_edits.append(SrcmlStmtInsertion)

class SrcmlConditionReplacement(AbstractXmlNodeReplacement):
    NODE_TAG = 'condition'

magpie.utils.known_edits.append(SrcmlConditionReplacement)

class SrcmlExprReplacement(AbstractXmlNodeReplacement):
    NODE_TAG = 'expr'

magpie.utils.known_edits.append(SrcmlExprReplacement)

class SrcmlComparisonOperatorSetting(AbstractXmlTextSetting):
    NODE_TAG = 'operator_comp'
    CHOICES = ['==', '!=', '<', '<=', '>', '>=']

magpie.utils.known_edits.append(SrcmlComparisonOperatorSetting)

class SrcmlArithmeticOperatorSetting(AbstractXmlTextSetting):
    NODE_TAG = 'operator_arith'
    CHOICES = ['+', '-', '*', '/', '%']

magpie.utils.known_edits.append(SrcmlArithmeticOperatorSetting)

class SrcmlNumericSetting(AbstractXmlTextSetting):
    NODE_TAG = 'number'
    CHOICES = ['-1', '0', '1']

magpie.utils.known_edits.append(SrcmlNumericSetting)

class SrcmlRelativeNumericSetting(AbstractXmlTextWrapping):
    NODE_TAG = 'number'
    CHOICES = [('(', '+1)'), ('(', '-1)'), ('(', '/2)'), ('(', '*2)'), ('(', '*3/2)'), ('(', '*2/3)')]

magpie.utils.known_edits.append(SrcmlRelativeNumericSetting)
