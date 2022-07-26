import re
from xml.etree import ElementTree

from . import XmlEngine

class SrcmlEngine(XmlEngine):
    INTERNODES = ['block']
    TAG_RENAME = {
        'stmt': {'break', 'continue', 'decl_stmt', 'do', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while'},
        'number': {'literal_number'}
    }
    TAG_FOCUS = {'block', 'stmt', 'operator_comp', 'operator_arith', 'number'}
    PROCESS_PSEUDO_BLOCKS = True
    PROCESS_LITERALS = True
    PROCESS_OPERATORS = True

    @classmethod
    def process_tree(cls, tree):
        if cls.PROCESS_PSEUDO_BLOCKS:
            cls.process_pseudo_blocks(tree)
        if cls.PROCESS_LITERALS:
            cls.process_literals(tree)
        if cls.PROCESS_OPERATORS:
            cls.process_operators(tree)
        for tag in cls.TAG_RENAME:
            cls.rewrite_tags(tree, cls.TAG_RENAME[tag], tag)
        if len(cls.TAG_FOCUS) > 0:
            cls.focus_tags(tree, cls.TAG_FOCUS)

    @classmethod
    def process_pseudo_blocks(cls, element, sp_element=''):
        sp = cls.guess_spacing(element.text)
        for child in element:
            cls.process_pseudo_blocks(child, sp)
            sp = cls.guess_spacing(child.tail)
        if element.tag == 'block' and element.attrib.get('type') == 'pseudo':
            del element.attrib['type']
            if len(element) > 0:
                element.text = '/*auto*/{' + (element.text or '')
                child.tail = (child.tail or '') + '\n' + sp_element + '}/*auto*/'
            else:
                element.text = '/*auto*/{' + (element.text or '') + '}/*auto*/'

    @classmethod
    def process_literals(cls, element):
        for child in element:
            cls.process_literals(child)
        if element.tag == 'literal':
            element.tag = 'literal_{}'.format(element.attrib.get('type'))
            del element.attrib['type']

    @classmethod
    def process_operators(cls, element):
        for child in element:
            cls.process_operators(child)
        if element.tag == 'operator':
            # TODO
            if element.text in ['==', '!=', '<', '<=', '>', '>=']:
                element.tag = 'operator_comp'
            elif element.text in ['+', '-', '*', '/']:
                element.tag = 'operator_arith'
            else:
                element.tag = 'operator_misc'
