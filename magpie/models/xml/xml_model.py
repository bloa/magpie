import copy
import re
import os
from xml.etree import ElementTree

from .abstract_model import AbstractXmlModel

class XmlModel(AbstractXmlModel):
    def __init__(self, filename):
        super().__init__(filename)
        self.config = {
            'internodes': [],
        }

    def init_contents(self):
        with open(self.filename) as target_file:
            tree = self.string_to_tree(target_file.read())
        self.contents = self.process_tree(tree)

        def aux(accu, prefix, root):
            if not self.config['internodes'] or root.tag in self.config['internodes']:
                if len(root) > 0: # can't deal with <block>{}</block>
                    for i in range(len(root)+1):
                        s = '{}><{}'.format(prefix, i) # "><" is safe because illegal
                        try:
                            accu['_inter_{}'.format(root.tag)].append(s)
                        except KeyError:
                            accu['_inter_{}'.format(root.tag)] = [s]
            tags = dict()
            for child in root:
                if child.tag in tags:
                    tags[child.tag] += 1
                else:
                    tags[child.tag] = 1
                s = '{}/{}[{}]'.format(prefix, child.tag, tags[child.tag])
                try:
                    accu[child.tag].append(s)
                except KeyError:
                    accu[child.tag] = [s]
                accu = aux(accu, s, child)
            return accu
        self.locations = aux({}, '.', tree)

    def process_tree(self, tree):
        return tree

    def dump(self):
        return self.strip_xml_from_tree(self.contents)

    def show_location(self, target_type, target_loc):
        out = '(unsupported target_type)'
        if target_type[:7] == '_inter_':
            fakepath = self.locations[target_type][target_loc]
            parent_xpath, insert_index = fakepath.split('><')
            insert_index = int(insert_index)
            parent = copy.deepcopy(self.contents.find(parent_xpath))
            sp = self.find_indent(parent_xpath)
            if insert_index == 0:
                parent.text = f'{parent.text or ""}\n(INSERTION POINT)\n{sp}'
            else:
                child = None
                tmp = {child.tag: 0 for child in parent}
                for i, child in enumerate(parent):
                    tmp[child.tag] += 1
                    if i == insert_index-1:
                        child_xpath = f'{parent_xpath}/{child.tag}[{tmp[child.tag]}]'
                        spc = self.find_indent(child_xpath)
                        child.tail = f'\n{spc}(INSERTION POINT){child.tail or ""}'
                        break
            out = '# {}: {}\n{}{}'.format(
                target_loc,
                fakepath,
                sp,
                self.tree_to_string(parent))
        else:
            xpath = self.locations[target_type][target_loc]
            sp = self.find_indent(xpath)
            out = '# {}: {}\n{}{}'.format(
                target_loc,
                xpath,
                sp,
                self.tree_to_string(self.contents.find(xpath), keep_tail=False))
        return out

    @staticmethod
    def string_to_tree(xml_str):
        xml_str = re.sub(r'(<[^>]+?)(?:\s+xmlns\w*="[^"]+")+', r'\1', xml_str, count=1)
        xml_str = re.sub(r'<(/?\w+?):(\w+)>', r'<\1_\2>', xml_str)
        return ElementTree.fromstring(xml_str)

    @staticmethod
    def tree_to_string(tree, keep_tail=True):
        if keep_tail:
            tmp = tree
        else:
            tmp = copy.deepcopy(tree)
            tmp.tail = None
        return ElementTree.tostring(tmp, encoding='unicode', method='xml')

    @staticmethod
    def strip_xml_from_tree(tree):
        return ''.join(tree.itertext())

    @staticmethod
    def split_xpath(xpath, prefix=None):
        if xpath == '.':
            raise ValueError()
        if prefix is None:
            pattern = re.compile(r'^(.*)/([^\[]+)(?:\[([^\]]+)\])?$')
            match = re.match(pattern, xpath)
            if match is None:
                raise LookupError()
            return (match.group(1), match.group(2), int(match.group(3)), None)
        else:
            if xpath[:len(prefix)+1] == prefix+'/':
                pattern = re.compile(r'^/([^\[]+)(?:\[([^\]]+)\])?(?:/(.*))?$')
                match = re.match(pattern, xpath[len(prefix):])
                if match is None:
                    raise LookupError()
                return (prefix, match.group(1), int(match.group(2)), match.group(3))
            else:
                return (None, None, None, None)

    def do_replace(self, ref_model, target_dest, target_orig):
        # get elements
        d_f, d_t, d_i = target_dest # file name, tag, xpath index
        o_f, o_t, o_i = target_orig # file name, tag, xpath index
        if d_f != self.filename: raise ValueError()
        if o_f != ref_model.filename: raise ValueError()
        target = self.contents.find(self.locations[d_t][d_i])
        ingredient = ref_model.contents.find(ref_model.locations[o_t][o_i])
        if target is None or ingredient is None:
            return False
        if self.tree_to_string(target, keep_tail=False) == self.tree_to_string(ingredient, keep_tail=False):
            return False

        # lookup indentations
        ind_t = self.find_indent(self.locations[d_t][d_i])
        ind_i = ref_model.find_indent(ref_model.locations[o_t][o_i])

        # mutate
        old_tag = target.tag
        old_tail = target.tail
        target.clear() # to remove children
        target.tag = ingredient.tag
        target.attrib = ingredient.attrib
        target.text = ingredient.text
        target.tail = old_tail
        for child in ingredient:
            target.append(copy.deepcopy(child))
        self.replace_indent(target, ind_t, ind_i)

        # update modification points
        if old_tag != ingredient.tag:
            head, tag, pos, _ = self.split_xpath(self.locations[d_t][d_i])
            itag = 1
            for i, xpath in enumerate(self.locations[d_t]):
                h, t, p, s = self.split_xpath(xpath, head)
                if i < d_i:
                    if h != head:
                        continue
                    elif t == ingredient.tag:
                        itag += 1
                elif i == d_i:
                    self.locations[d_t][i] = '{}/{}[{}]'.format(h, ingredient.tag, itag)
                elif h != head:
                    break
                elif t == tag:
                    if p == pos:
                        new_pos = 'deleted'
                    elif s:
                        new_pos = '{}/{}[{}]/{}'.format(h, t, p-1, s)
                    else:
                        new_pos = '{}/{}[{}]'.format(h, t, p-1)
                    self.locations[d_t][i] = new_pos
                elif t == ingredient.tag:
                    if s:
                        new_pos = '{}/{}[{}]/{}'.format(h, t, p+1, s)
                    else:
                        new_pos = '{}/{}[{}]'.format(h, t, p+1)
                    self.locations[o_t][i] = new_pos
        xpath = self.locations[d_t][d_i]
        for i, xpath_inter in enumerate(self.locations[d_t]):
            if xpath_inter > xpath and xpath_inter[:len(xpath)] == xpath:
                self.locations[d_t][i] = 'deleted'
        return True

    def do_insert(self, ref_model, target_dest, target_orig):
        # get elements
        d_f, d_t, d_i = target_dest # file name, tag, xpath index
        o_f, o_t, o_i = target_orig # file name, tag, xpath index
        if d_f != self.filename: raise ValueError()
        if o_f != ref_model.filename: raise ValueError()
        parent_xpath, insert_index = self.locations[d_t][d_i].split('><')
        insert_index = int(insert_index)
        parent = self.contents.find(parent_xpath)
        ingredient = ref_model.contents.find(ref_model.locations[o_t][o_i])
        if parent is None or ingredient is None:
            return False

        # lookup indentations
        for child in parent:
            ind_t = self.find_indent(f'{parent_xpath}/{child.tag}[1]')
            break
        else:
            ind_t = '  ' # no idea?!
        ind_i = ref_model.find_indent(ref_model.locations[o_t][o_i])

        # mutate
        tmp = copy.deepcopy(ingredient)
        if insert_index == 0:
            tmp.tail = f'\n{ind_t}'
            parent.insert(insert_index, tmp)
        else:
            child = None
            for i, child in enumerate(parent):
                if i == insert_index-1:
                    tmp.tail = child.tail
                    child.tail = f'\n{ind_t}'
                    parent.insert(insert_index, tmp)
                    break
            else:
                tmp.tail = child.tail
                child.tail = f'\n{ind_t}'
                parent.insert(i+1, tmp)
        self.replace_indent(tmp, ind_t, ind_i)

        # update modification points
        for i, xpath in enumerate(self.locations[o_t]):
            if xpath == 'deleted':
                continue
            h, t, p, s = self.split_xpath(xpath, parent_xpath)
            if h != parent_xpath or t != ingredient.tag or p < insert_index:
                continue
            if s:
                new_pos = '{}/{}[{}]/{}'.format(h, t, p+1, s)
            else:
                new_pos = '{}/{}[{}]'.format(h, t, p+1)
            self.locations[o_t][i] = new_pos
        for i, xpath_inter in enumerate(self.locations[d_t]):
            xpath, index = xpath_inter.split('><')
            index = int(index)
            if xpath != parent_xpath or index < insert_index:
                continue
            self.locations[d_t][i] = '{}><{}'.format(xpath, index+1)
        return True

    def do_delete(self, target):
        # get elements
        d_f, d_t, d_i = target # file name, tag, xpath index
        if d_f != self.filename: raise ValueError()
        target = self.contents.find(self.locations[d_t][d_i])
        if target is None:
            return False
        if len(target) == 0 and target.text == None: # (probably) already deleted
            return False

        # mutate
        old_tag = target.tag
        old_tail = target.tail
        target.clear() # to remove children
        target.tag = old_tag
        target.tail = old_tail
        return True

    def do_set_text(self, target, value):
        d_f, d_t, d_i = target # file name, tag, xpath index
        if d_f != self.filename: raise ValueError()
        target = self.contents.find(self.locations[d_t][d_i])
        if target is None or target.text == value:
            return False
        target.text = value
        return True

    def do_wrap_text(self, target, prefix, suffix):
        d_f, d_t, d_i = target # file name, tag, xpath index
        if d_f != self.filename: raise ValueError()
        target = self.contents.find(self.locations[d_t][d_i])
        if target is None:
            return False
        target.text = prefix + (target.text or '') + suffix
        return True

    def focus_tags(self, element, tags):
        last = None
        marked = []
        for i, child in enumerate(element):
            self.focus_tags(child, tags)
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

    def remove_tags(self, element, tags):
        if len(tags) == 0:
            return
        last = None
        marked = []
        remove_all = '*' in tags
        for i, child in enumerate(element):
            self.remove_tags(child, tags)
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

    def get_tags(self, element):
        def aux(element, accu):
            accu.append(element.tag)
            for child in element:
                aux(child, accu)
            return set(accu)
        return aux(element, [])

    def count_tags(self, element):
        def aux(element, accu):
            try:
                accu[element.tag] += 1
            except KeyError:
                accu[element.tag] = 1
            for child in element:
                aux(child, accu)
            return accu
        return aux(element, {})

    def rewrite_tags(self, element, tags, new_tag):
        if element.tag in tags:
            element.tag = new_tag
        for child in element:
            self.rewrite_tags(child, tags, new_tag)

    def rotate_newlines(self, element):
        if element.tail:
            match = re.match(r'(^\n\s*)', element.tail)
            if match:
                element.tail = element.tail[len(match.group(1)):]
                if len(element) > 0:
                    element[-1].tail = element[-1].tail or ''
                    element[-1].tail += match.group(1)
                else:
                    element.text = element.text or ''
                    element.text += match.group(1)
        for child in element:
            self.rotate_newlines(child)

    def find_indent(self, xpath):
        if xpath == '.':
            return ''

        def aux(root, xpath):
            m = re.match(r'^(.*)\/[^\[]+\[(\d+)\]$', xpath)
            target = root.find(xpath)
            parent = root.find(m.groups()[0])
            if target is None:
                breakpoint()
            assert target is not None
            if parent is root:
                return ''
            index = int(m.groups()[1])
            if index == 1:
                parent_lead = parent.text
            else:
                for child in parent:
                    if child is target:
                        break
                    parent_lead = child.tail
                else:
                    assert False
            if parent_lead:
                if '\n' in parent_lead:
                    lead = parent_lead.split('\n')[-1]
                    lead = re.match(r'^(\s*)', lead).groups()[0]
                    return lead
            lead = self.find_indent(m.groups()[0]) + (parent_lead or '')
            lead = re.match(r'^(\s*)', lead).groups()[0]
            return lead

        return aux(self.contents, xpath)

    def replace_indent(self, target, ind_t, ind_i, _first=True):
        if target.text:
            target.text = target.text.replace(f'\n{ind_i}', f'\n{ind_t}')
        if target.tail and not _first:
            target.tail = target.tail.replace(f'\n{ind_i}', f'\n{ind_t}')
        for child in target:
            self.replace_indent(child, ind_t, ind_i, False)
