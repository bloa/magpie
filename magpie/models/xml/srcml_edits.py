import magpie.utils

from .xml_edits import (
    XmlNodeDeletionTemplatedEdit,
    XmlNodeInsertionTemplatedEdit,
    XmlNodeReplacementTemplatedEdit,
    XmlTextSettingTemplatedEdit,
    XmlTextWrappingTemplatedEdit,
)


class XmlLineDeletionEdit(XmlNodeDeletionTemplatedEdit):
    TEMPLATE = ('line',)

magpie.utils.known_edits.append(XmlLineDeletionEdit)

class XmlLineReplacementEdit(XmlNodeReplacementTemplatedEdit):
    TEMPLATE = ('line',)

magpie.utils.known_edits.append(XmlLineReplacementEdit)

class XmlLineInsertionEdit(XmlNodeInsertionTemplatedEdit):
    TEMPLATE = ('line', 'unit')

magpie.utils.known_edits.append(XmlLineInsertionEdit)

class SrcmlStmtDeletionEdit(XmlNodeDeletionTemplatedEdit):
    TEMPLATE = ('stmt',)

magpie.utils.known_edits.append(SrcmlStmtDeletionEdit)

class SrcmlStmtReplacementEdit(XmlNodeReplacementTemplatedEdit):
    TEMPLATE = ('stmt',)

magpie.utils.known_edits.append(SrcmlStmtReplacementEdit)

class SrcmlStmtInsertionEdit(XmlNodeInsertionTemplatedEdit):
    TEMPLATE = ('stmt', 'block')

magpie.utils.known_edits.append(SrcmlStmtInsertionEdit)

class SrcmlConditionReplacementEdit(XmlNodeReplacementTemplatedEdit):
    TEMPLATE = ('condition',)

magpie.utils.known_edits.append(SrcmlConditionReplacementEdit)

class SrcmlExprReplacementEdit(XmlNodeReplacementTemplatedEdit):
    TEMPLATE = ('expr',)

magpie.utils.known_edits.append(SrcmlExprReplacementEdit)

class SrcmlComparisonOperatorSettingEdit(XmlTextSettingTemplatedEdit):
    TEMPLATE = ('operator_comp', '==', '!=', '<', '<=', '>', '>=')

magpie.utils.known_edits.append(SrcmlComparisonOperatorSettingEdit)

class SrcmlArithmeticOperatorSettingEdit(XmlTextSettingTemplatedEdit):
    TEMPLATE = ('operator_arith', '+', '-', '*', '/', '%')

magpie.utils.known_edits.append(SrcmlArithmeticOperatorSettingEdit)

class SrcmlNumericSettingEdit(XmlTextSettingTemplatedEdit):
    TEMPLATE = ('number', '-1', '0', '1')

magpie.utils.known_edits.append(SrcmlNumericSettingEdit)

class SrcmlRelativeNumericSettingEdit(XmlTextWrappingTemplatedEdit):
    TEMPLATE = ('number',
                '(', '+1)', '(', '-1)',
                '(', '/2)', '(', '*2)',
                '(', '*3/2)', '(', '*2/3)')

magpie.utils.known_edits.append(SrcmlRelativeNumericSettingEdit)
