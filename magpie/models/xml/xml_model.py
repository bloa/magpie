import copy
import pathlib
import re
from xml.etree import ElementTree

import magpie.utils

from .abstract_model import AbstractXmlModel


class XmlModel(AbstractXmlModel):
    def __init__(self, filename):
        super().__init__(filename)
        self.config = {
            'internodes': [],
        }

    def setup(self, config, section_name):
        super().setup(config, section_name)
        config_section = config[section_name]
        if (k := 'internodes') in config_section:
            self.config[k] = set(config_section[k].split())

    def init_contents(self):
        with pathlib.Path(self.filename).open('r') as target_file:
            tree = self.string_to_tree(target_file.read())
        self.contents = self.process_tree(tree)

        def aux(accu, prefix, root):
            if not self.config['internodes'] or root.tag in self.config['internodes']:
                if len(root) > 0: # can't deal with <block>{}</block>
                    for i in range(len(root)+1):
                        s = f'{prefix}><{i}' # "><" is safe because illegal
                        try:
                            accu[f'_inter_{root.tag}'].append(s)
                        except KeyError:
                            accu[f'_inter_{root.tag}'] = [s]
            tags = {}
            for child in root:
                if child.tag in tags:
                    tags[child.tag] += 1
                else:
                    tags[child.tag] = 1
                s = f'{prefix}/{child.tag}[{tags[child.tag]}]'
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
        insert = '(INSERTION POINT)'
        tag_start = '# '
        tag_middle = ': '
        tag_end = '\n'
        if magpie.settings.color_output:
            insert = f'\033[32m{insert}\033[0m'
            tag_start = f'\033[36m{tag_start}'
            tag_middle = f'{tag_middle}\033[34m'
            tag_end = f'{tag_end}\033[0m'
        if target_type[:7] == '_inter_':
            fakepath = self.locations[target_type][target_loc]
            parent_xpath, insert_index = fakepath.split('><')
            insert_index = int(insert_index)
            parent = copy.deepcopy(self.contents.find(parent_xpath))
            sp = self.find_indent(parent_xpath)
            if insert_index == 0:
                parent.text = f'{parent.text or ""}\n{insert}\n{sp}'
            else:
                child = None
                tmp = {child.tag: 0 for child in parent}
                for i, child in enumerate(parent):
                    tmp[child.tag] += 1
                    if i == insert_index-1:
                        child_xpath = f'{parent_xpath}/{child.tag}[{tmp[child.tag]}]'
                        spc = self.find_indent(child_xpath)
                        child.tail = f'\n{spc}{insert}{child.tail or ""}'
                        break
            tmp = self.tree_to_string(parent)
            return f'{tag_start}{target_loc}{tag_middle}{fakepath}{tag_end}{sp}{tmp}'
        # default: non '_inter_' tag
        xpath = self.locations[target_type][target_loc]
        sp = self.find_indent(xpath)
        tmp = self.tree_to_string(self.contents.find(xpath), keep_tail=False)
        return f'{tag_start}{target_loc}{tag_middle}{xpath}{tag_end}{sp}{tmp}'

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
            raise ValueError
        if prefix is None:
            pattern = re.compile(r'^(.*)/([^\[]+)(?:\[([^\]]+)\])?$')
            match = re.match(pattern, xpath)
            if match is None:
                raise LookupError
            return (match.group(1), match.group(2), int(match.group(3)), None)
        if xpath[:len(prefix)+1] == prefix+'/':
            pattern = re.compile(r'^/([^\[]+)(?:\[([^\]]+)\])?(?:/(.*))?$')
            match = re.match(pattern, xpath[len(prefix):])
            if match is None:
                raise LookupError
            return (prefix, match.group(1), int(match.group(2)), match.group(3))
        return (None, None, None, None)

    def do_replace(self, ref_model, target_dest, target_orig):
        # get elements
        d_f, d_t, d_i = target_dest # file name, tag, xpath index
        o_f, o_t, o_i = target_orig # file name, tag, xpath index
        if (d_f != self.filename or
            o_f != ref_model.filename):
            raise ValueError
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
                    if t == ingredient.tag:
                        itag += 1
                elif i == d_i:
                    self.locations[d_t][i] = f'{h}/{ingredient.tag}[{itag}]'
                elif h != head:
                    break
                elif t == tag:
                    if p == pos:
                        new_pos = 'deleted'
                    elif s:
                        new_pos = f'{h}/{t}[{p-1}]/{s}'
                    else:
                        new_pos = f'{h}/{t}[{p-1}]'
                    self.locations[d_t][i] = new_pos
                elif t == ingredient.tag:
                    if s:
                        new_pos = f'{h}/{t}[{p+1}]/{s}'
                    else:
                        new_pos = f'{h}/{t}[{p+1}]'
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
        if (d_f != self.filename or
            o_f != ref_model.filename):
            raise ValueError
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
                new_pos = f'{h}/{t}[{p+1}]/{s}'
            else:
                new_pos = f'{h}/{t}[{p+1}]'
            self.locations[o_t][i] = new_pos
        for i, xpath_inter in enumerate(self.locations[d_t]):
            xpath, index = xpath_inter.split('><')
            index = int(index)
            if xpath != parent_xpath or index < insert_index:
                continue
            self.locations[d_t][i] = f'{xpath}><{index+1}'
        return True

    def do_delete(self, target):
        # get elements
        d_f, d_t, d_i = target # file name, tag, xpath index
        if d_f != self.filename:
            raise ValueError
        target = self.contents.find(self.locations[d_t][d_i])
        if target is None:
            return False
        if len(target) == 0 and target.text is None: # (probably) already deleted
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
        if d_f != self.filename:
            raise ValueError
        target = self.contents.find(self.locations[d_t][d_i])
        if target is None or target.text == value:
            return False
        target.text = value
        return True

    def do_wrap_text(self, target, prefix, suffix):
        d_f, d_t, d_i = target # file name, tag, xpath index
        if d_f != self.filename:
            raise ValueError
        target = self.contents.find(self.locations[d_t][d_i])
        if target is None:
            return False
        target.text = prefix + (target.text or '') + suffix
        return True

    def find_indent(self, xpath):
        if xpath == '.':
            return ''

        def aux(root, xpath):
            m = re.match(r'^(.*)\/[^\[]+\[(\d+)\]$', xpath)
            target = root.find(xpath)
            parent = root.find(m.groups()[0])
            if target is None:
                raise AssertionError
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
                    raise RuntimeError
            if parent_lead and '\n' in parent_lead:
                lead = parent_lead.split('\n')[-1]
                return re.match(r'^(\s*)', lead).groups()[0]
            lead = self.find_indent(m.groups()[0]) + (parent_lead or '')
            return re.match(r'^(\s*)', lead).groups()[0]

        return aux(self.contents, xpath)

    def replace_indent(self, target, ind_t, ind_i, _first=True):
        if target.text:
            target.text = target.text.replace(f'\n{ind_i}', f'\n{ind_t}')
        if target.tail and not _first:
            target.tail = target.tail.replace(f'\n{ind_i}', f'\n{ind_t}')
        for child in target:
            self.replace_indent(child, ind_t, ind_i, False)

magpie.utils.known_models.append(XmlModel)
