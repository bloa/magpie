from .xml_edits import NodeDeletion, NodeReplacement, NodeInsertion, NodeMoving
from .xml_edits import TextSetting, TextWrapping

class XmlLineDeletion(NodeDeletion):
    NODE_TYPE = 'line'

class XmlLineReplacement(NodeReplacement):
    NODE_TYPE = 'line'

class XmlLineInsertion(NodeInsertion):
    NODE_PARENT_TYPE = 'unit'
    NODE_TYPE = 'line'

class XmlLineMoving(NodeMoving):
    NODE_PARENT_TYPE = 'unit'
    NODE_TYPE = 'line'

class StmtDeletion(NodeDeletion):
    NODE_TYPE = 'stmt'

class StmtReplacement(NodeReplacement):
    NODE_TYPE = 'stmt'

class StmtInsertion(NodeInsertion):
    NODE_PARENT_TYPE = 'block'
    NODE_TYPE = 'stmt'

class StmtMoving(NodeMoving):
    NODE_PARENT_TYPE = 'block'
    NODE_TYPE = 'stmt'

class ConditionReplacement(NodeReplacement):
    NODE_TYPE = 'condition'

class ExprReplacement(NodeReplacement):
    NODE_TYPE = 'expr'

class ComparisonOperatorSetting(TextSetting):
    NODE_TYPE = 'operator_comp'
    CHOICES = ['==', '!=', '<', '<=', '>', '>=']

class ArithmeticOperatorSetting(TextSetting):
    NODE_TYPE = 'operator_arith'
    CHOICES = ['+', '-', '*', '/', '%']

class NumericSetting(TextSetting):
    NODE_TYPE = 'number'
    CHOICES = ['-1', '0', '1']

class RelativeNumericSetting(TextWrapping):
    NODE_TYPE = 'number'
    CHOICES = [('(', '+1)'), ('(', '-1)'), ('(', '/2)'), ('(', '*2)'), ('(', '*3/2)'), ('(', '*2/3)')]
