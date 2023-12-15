from .xml_edits import AbstractXmlNodeDeletion, AbstractXmlNodeReplacement, AbstractXmlNodeInsertion
from .xml_edits import AbstractXmlTextSetting, AbstractXmlTextWrapping

class XmlLineDeletion(AbstractXmlNodeDeletion):
    NODE_TAG = 'line'

class XmlLineReplacement(AbstractXmlNodeReplacement):
    NODE_TAG = 'line'

class XmlLineInsertion(AbstractXmlNodeInsertion):
    NODE_PARENT_TAG = 'unit'
    NODE_TAG = 'line'

class SrcmlStmtDeletion(AbstractXmlNodeDeletion):
    NODE_TAG = 'stmt'

class SrcmlStmtReplacement(AbstractXmlNodeReplacement):
    NODE_TAG = 'stmt'

class SrcmlStmtInsertion(AbstractXmlNodeInsertion):
    NODE_PARENT_TAG = 'block'
    NODE_TAG = 'stmt'

class SrcmlConditionReplacement(AbstractXmlNodeReplacement):
    NODE_TAG = 'condition'

class SrcmlExprReplacement(AbstractXmlNodeReplacement):
    NODE_TAG = 'expr'

class SrcmlComparisonOperatorSetting(AbstractXmlTextSetting):
    NODE_TAG = 'operator_comp'
    CHOICES = ['==', '!=', '<', '<=', '>', '>=']

class SrcmlArithmeticOperatorSetting(AbstractXmlTextSetting):
    NODE_TAG = 'operator_arith'
    CHOICES = ['+', '-', '*', '/', '%']

class SrcmlNumericSetting(AbstractXmlTextSetting):
    NODE_TAG = 'number'
    CHOICES = ['-1', '0', '1']

class SrcmlRelativeNumericSetting(AbstractXmlTextWrapping):
    NODE_TAG = 'number'
    CHOICES = [('(', '+1)'), ('(', '-1)'), ('(', '/2)'), ('(', '*2)'), ('(', '*3/2)'), ('(', '*2/3)')]
