import re
from xml.etree import ElementTree

from . import XmlEngine

class SrcmlEngine(XmlEngine):
    INTERNODES = {'block'}
    TAG_RENAME = {
        'stmt': {'break', 'continue', 'decl_stmt', 'do', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while'},
        'number': {'literal_number'}
    }
    TAG_FOCUS = {'block', 'stmt', 'operator_comp', 'operator_arith', 'number'}
    PROCESS_PSEUDO_BLOCKS = True
    PROCESS_LITERALS = True
    PROCESS_OPERATORS = True

    def __init__(self):
        self.config = {
            'internodes': self.INTERNODES,
            'tag_rename': self.TAG_RENAME,
            'tag_focus': self.TAG_FOCUS,
            'process_pseudo_blocks': self.PROCESS_PSEUDO_BLOCKS,
            'process_literals': self.PROCESS_LITERALS,
            'process_operators': self.PROCESS_OPERATORS,
        }

    def process_tree(self, tree):
        if self.config['process_pseudo_blocks']:
            self.process_pseudo_blocks(tree)
        if self.config['process_literals']:
            self.process_literals(tree)
        if self.config['process_operators']:
            self.process_operators(tree)
        for tag in self.config['tag_rename']:
            self.rewrite_tags(tree, self.config['tag_rename'][tag], tag)
        if len(self.config['tag_focus']) > 0:
            self.focus_tags(tree, self.config['tag_focus'])

    def guess_spacing(self, text):
        if text is None:
            return ''
        m = [''] + re.findall(r"\n(\s*)", text, re.MULTILINE)
        return m[-1]

    def process_pseudo_blocks(self, element, sp_parent='', step_parent=0):
        sp = max(sp_parent, self.guess_spacing(element.text))
        for child in element:
            step = len(sp) - len(sp_parent)
            if step == 0:
                step = step_parent
            self.process_pseudo_blocks(child, sp, step)
            sp = max(sp, self.guess_spacing(child.tail))
        if element.tag == 'block' and element.attrib.get('type') == 'pseudo':
            del element.attrib['type']
            if len(element) > 0:
                element.text = '/*auto*/{\n' + sp_parent + (element.text or '') + ' '*step
                child.tail = (child.tail or '') + '\n' + sp_parent + '}/*auto*/'
            else:
                element.text = '/*auto*/{\n' + sp_parent + (element.text or '') + '\n' + sp_parent + '}/*auto*/'

    def process_literals(self, element):
        for child in element:
            self.process_literals(child)
        if element.tag == 'literal':
            element.tag = 'literal_{}'.format(element.attrib.get('type'))
            del element.attrib['type']

    def process_operators(self, element):
        for child in element:
            self.process_operators(child)
        if element.tag == 'operator':
            # TODO
            if element.text in ['==', '!=', '<', '<=', '>', '>=']:
                element.tag = 'operator_comp'
            elif element.text in ['+', '-', '*', '/']:
                element.tag = 'operator_arith'
            else:
                element.tag = 'operator_misc'
