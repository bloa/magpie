import re

import magpie.utils

from .xml_model import XmlModel


class SrcmlModel(XmlModel):
    def __init__(self, filename):
        super().__init__(filename)
        self.renamed_filename = filename.split('.xml')[0]
        self.config = {
            'internodes': {'block'},
            'tag_rename': {
                'stmt': {'break', 'continue', 'decl_stmt', 'do', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while'},
                'number': {'literal_number'},
            },
            'tag_focus': {'block', 'stmt', 'operator_comp', 'operator_arith', 'number'},
            'process_pseudo_blocks': True,
            'process_literals': True,
            'process_operators': True,
        }

    def setup(self, config, section_name):
        super().setup(config, section_name)
        for name in tuple({'srcml', section_name}):
            config_section = config[name]
            for k in [
                    'process_pseudo_blocks',
                    'process_literals',
                    'process_operators',
            ]:
                val = config_section[k]
                if val.lower() in ['true', 't', '1']:
                    self.config[k] = True
                elif val.lower() in ['false', 'f', '0']:
                    self.config[k] = False
                else:
                    msg = f'Invalid config file: "{name} {k}" should be Boolean'
                    raise magpie.core.ScenarioError(msg)
            if 'rename' in config_section:
                h = {}
                try:
                    for rule in config_section['rename'].split('\n'):
                        if rule.strip(): # discard potential initial empty line
                            k, v = rule.split(':')
                            h[k] = set(v.split())
                except ValueError as e:
                    msg = f'Badly formated rule: "{rule}"'
                    raise magpie.core.ScenarioError(msg) from e
                self.config['tag_rename'] = h
            if 'focus' in config_section:
                self.config['tag_focus'] = set(config_section['focus'].split())

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
        return tree

    @staticmethod
    def guess_spacing(text):
        if text is None:
            return ''
        m = ['', *re.findall(r'\n(\s*)', text, re.MULTILINE)]
        return m[-1]

    @staticmethod
    def process_pseudo_blocks(element, sp_parent='', step_parent=0):
        sp = max(sp_parent, SrcmlModel.guess_spacing(element.text))
        for child in element:
            step = len(sp) - len(sp_parent)
            if step == 0:
                step = step_parent
            SrcmlModel.process_pseudo_blocks(child, sp, step)
            sp = max(sp, SrcmlModel.guess_spacing(child.tail))
        if element.tag == 'block' and element.attrib.get('type') == 'pseudo':
            del element.attrib['type']
            if len(element) > 0:
                element.text = '/*auto*/{\n' + sp_parent + (element.text or '') + ' '*step
                child.tail = (child.tail or '') + '\n' + sp_parent + '}/*auto*/'
            else:
                element.text = '/*auto*/{\n' + sp_parent + (element.text or '') + '\n' + sp_parent + '}/*auto*/'

    @staticmethod
    def process_literals(element):
        for child in element:
            SrcmlModel.process_literals(child)
        if element.tag == 'literal':
            element.tag = f"literal_{element.attrib.get('type')}"
            del element.attrib['type']

    @staticmethod
    def process_operators(element):
        for child in element:
            SrcmlModel.process_operators(child)
        if element.tag == 'operator':
            # TODO
            if element.text in ['==', '!=', '<', '<=', '>', '>=']:
                element.tag = 'operator_comp'
            elif element.text in ['+', '-', '*', '/']:
                element.tag = 'operator_arith'
            else:
                element.tag = 'operator_misc'

    @staticmethod
    def focus_tags(element, tags):
        last = None
        marked = []
        for i, child in enumerate(element):
            SrcmlModel.focus_tags(child, tags)
            if child.tag not in tags:
                marked.append(child)
                if child.text:
                    if last is not None:
                        last.tail = (last.tail or '') + child.text
                    else:
                        element.text = (element.text or '') + child.text
                if len(child) > 0:
                    for sub_child in reversed(child):
                        element.insert(i+1, sub_child)
                    last = child[-1]
                if child.tail:
                    if last is not None:
                        last.tail = (last.tail or '') + child.tail
                    else:
                        element.text = (element.text or '') + child.tail
            else:
                last = child
        for child in marked:
            element.remove(child)

    @staticmethod
    def remove_tags(element, tags):
        if len(tags) == 0:
            return
        last = None
        marked = []
        remove_all = '*' in tags
        for i, child in enumerate(element):
            SrcmlModel.remove_tags(child, tags)
            if remove_all or child.tag in tags:
                marked.append(child)
                if child.text:
                    if last is not None:
                        last.tail = (last.tail or '') + child.text
                    else:
                        element.text = (element.text or '') + child.text
                if len(child) > 0:
                    for sub_child in reversed(child):
                        element.insert(i+1, sub_child)
                    last = child[-1]
                if child.tail:
                    if last is not None:
                        last.tail = (last.tail or '') + child.tail
                    else:
                        element.text = (element.text or '') + child.tail
            else:
                last = child
        for child in marked:
            element.remove(child)

    @staticmethod
    def rewrite_tags(element, tags, new_tag):
        if element.tag in tags:
            element.tag = new_tag
        for child in element:
            SrcmlModel.rewrite_tags(child, tags, new_tag)

magpie.utils.known_models.append(SrcmlModel)
