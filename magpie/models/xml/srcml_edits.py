from .xml_edits import XmlNodeDeletion, XmlNodeReplacement, XmlNodeInsertion
from .xml_edits import XmlTextSetting, XmlTextWrapping

class XmlLineDeletion(XmlNodeDeletion):
    NODE_TAG = 'line'

class XmlLineReplacement(XmlNodeReplacement):
    NODE_TAG = 'line'

class XmlLineInsertion(XmlNodeInsertion):
    NODE_PARENT_TAG = 'unit'
    NODE_TAG = 'line'

class SrcmlStmtDeletion(XmlNodeDeletion):
    NODE_TAG = 'stmt'

class SrcmlStmtReplacement(XmlNodeReplacement):
    NODE_TAG = 'stmt'

class SrcmlStmtInsertion(XmlNodeInsertion):
    NODE_PARENT_TAG = 'block'
    NODE_TAG = 'stmt'

class SrcmlConditionReplacement(XmlNodeReplacement):
    NODE_TAG = 'condition'

class SrcmlExprReplacement(XmlNodeReplacement):
    NODE_TAG = 'expr'

class SrcmlComparisonOperatorSetting(XmlTextSetting):
    NODE_TAG = 'operator_comp'
    CHOICES = ['==', '!=', '<', '<=', '>', '>=']

class SrcmlArithmeticOperatorSetting(XmlTextSetting):
    NODE_TAG = 'operator_arith'
    CHOICES = ['+', '-', '*', '/', '%']

class SrcmlNumericSetting(XmlTextSetting):
    NODE_TAG = 'number'
    CHOICES = ['-1', '0', '1']

class SrcmlRelativeNumericSetting(XmlTextWrapping):
    NODE_TAG = 'number'
    CHOICES = [('(', '+1)'), ('(', '-1)'), ('(', '/2)'), ('(', '*2)'), ('(', '*3/2)'), ('(', '*2/3)')]
