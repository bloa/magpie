import copy
import re
import os
from . import AbstractTreeEngine
from xml.etree import ElementTree

class XmlEngine(AbstractTreeEngine):
    INTERNODES = []

    @classmethod
    def process_tree(cls, tree):
        pass

    @classmethod
    def get_contents(cls, file_path):
        with open(file_path) as target_file:
            tree = cls.string_to_tree(target_file.read())
        cls.process_tree(tree)
        return tree

    @classmethod
    def get_locations(cls, contents_of_file):
        def aux(accu, prefix, root):
            if not cls.INTERNODES or root.tag in cls.INTERNODES:
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
        return aux({}, '.', contents_of_file)

    @classmethod
    def write_to_tmp_dir(cls, contents_of_file, tmp_path):
        root, ext = os.path.splitext(tmp_path)
        if ext != '.xml':
            raise ValueError()
        super().write_to_tmp_dir(contents_of_file, root)

    @classmethod
    def reset_in_tmp_dir(cls, target_file, ref_path, tmp_path):
        root, ext = os.path.splitext(target_file)
        if ext != '.xml':
            raise ValueError()
        super().reset_in_tmp_dir(root, ref_path, tmp_path)

    @classmethod
    def dump(cls, contents_of_file):
        return cls.strip_xml_from_tree(contents_of_file)

    @staticmethod
    def string_to_tree(s):
        xml = re.sub(r'(?:\s+xmlns[^=]*="[^"]+")+', '', s, count=1)
        xml = re.sub(r'<(/?)[^>]+:([^:>]+)>', r'<\1\2>', xml)
        try:
            return ElementTree.fromstring(xml)
        except ElementTree.ParseError as e:
            raise Exception('Program', 'ParseError: {}'.format(str(e))) from None

    @staticmethod
    def tree_to_string(tree):
        return ElementTree.tostring(tree, encoding='unicode', method='xml')

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

    @classmethod
    def do_replace(cls, contents, locations, new_contents, new_locations, target_dest, target_orig):
        # get elements
        d_f, d_t, d_i = target_dest # file name, tag, xpath index
        o_f, o_t, o_i = target_orig # file name, tag, xpath index
        target = new_contents[d_f].find(new_locations[d_f][d_t][d_i])
        ingredient = contents[o_f].find(locations[o_f][o_t][o_i])
        if target is None or ingredient is None:
            return False
        if cls.tree_to_string(target) == cls.tree_to_string(ingredient):
            return False

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

        # update modification points
        if old_tag != ingredient.tag:
            head, tag, pos, _ = cls.split_xpath(new_locations[d_f][d_t][d_i])
            itag = 1
            for i, xpath in enumerate(new_locations[d_f][d_t]):
                h, t, p, s = cls.split_xpath(xpath, head)
                if i < d_i:
                    if h != head:
                        continue
                    elif t == ingredient.tag:
                        itag += 1
                elif i == d_i:
                    new_locations[d_f][i] = '{}/{}[{}]'.format(h, ingredient.tag, itag)
                elif h != head:
                    break
                elif t == tag:
                    if p == pos:
                        new_pos = 'deleted'
                    elif s:
                        new_pos = '{}/{}[{}]/{}'.format(h, t, p-1, s)
                    else:
                        new_pos = '{}/{}[{}]'.format(h, t, p-1)
                    new_locations[d_f][i] = new_pos
                elif t == ingredient.tag:
                    if s:
                        new_pos = '{}/{}[{}]/{}'.format(h, t, p+1, s)
                    else:
                        new_pos = '{}/{}[{}]'.format(h, t, p+1)
                    new_locations[d_f][i] = new_pos
        xpath = new_locations[d_f][d_t][d_i]
        for i, xpath_inter in enumerate(new_locations[d_f][d_t]):
            if xpath_inter[:len(xpath)] == xpath:
                new_locations[d_f][d_t][i] = 'deleted'
        return True

    @classmethod
    def do_insert(cls, contents, locations, new_contents, new_locations, target_dest, target_orig):
        # get elements
        d_f, d_t, d_i = target_dest # file name, tag, xpath index
        o_f, o_t, o_i = target_orig # file name, tag, xpath index
        if new_locations[d_f][d_t][d_i] == 'deleted':
            return False
        parent_xpath, insert_index = new_locations[d_f][d_t][d_i].split('><')
        insert_index = int(insert_index)
        parent = new_contents[d_f].find(parent_xpath)
        ingredient = contents[o_f].find(locations[o_f][o_t][o_i])
        if parent is None or ingredient is None:
            return False

        # mutate
        sp = cls.guess_spacing(parent.text)
        tmp = copy.deepcopy(ingredient)
        if insert_index == 0:
            tmp.tail = "\n" + sp
            parent.insert(insert_index, tmp)
        else:
            child = None
            for i, child in enumerate(parent):
                if i == insert_index-1:
                    tmp.tail = child.tail
                    child.tail = "\n" + sp
                    parent.insert(insert_index, tmp)
                    break
                sp = cls.guess_spacing(child.tail)
            else:
                tmp.tail = child.tail
                child.tail = "\n" + sp
                parent.insert(i+1, tmp)
                # raise RuntimeError

        # update modification points
        for i, xpath in enumerate(new_locations[d_f][o_t]):
            if xpath == 'deleted':
                continue
            h, t, p, s = cls.split_xpath(xpath, parent_xpath)
            if h != parent_xpath or t != ingredient.tag or p < insert_index:
                continue
            if s:
                new_pos = '{}/{}[{}]/{}'.format(h, t, p+1, s)
            else:
                new_pos = '{}/{}[{}]'.format(h, t, p+1)
            new_locations[d_f][o_t][i] = new_pos
        for i, xpath_inter in enumerate(new_locations[d_f][d_t]):
            xpath, index = xpath_inter.split('><')
            index = int(index)
            if xpath != parent_xpath or index < insert_index:
                continue
            new_locations[d_f][d_t][i] = '{}><{}'.format(xpath, index+1)
        return True

    @classmethod
    def do_delete(cls, contents, locations, new_contents, new_locations, target):
        # get elements
        d_f, d_t, d_i = target # file name, tag, xpath index
        target = new_contents[d_f].find(new_locations[d_f][d_t][d_i])
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

    @classmethod
    def do_set_text(cls, contents, locations, new_contents, new_locations, target, value):
        d_f, d_t, d_i = target # file name, tag, xpath index
        target = new_contents[d_f].find(new_locations[d_f][d_t][d_i])
        if target is None or target.text == value:
            return False
        else:
            target.text = value
            return True

    @classmethod
    def do_wrap_text(cls, contents, locations, new_contents, new_locations, target, prefix, suffix):
        d_f, d_t, d_i = target # file name, tag, xpath index
        target = new_contents[d_f].find(new_locations[d_f][d_t][d_i])
        if target is None:
            return False
        else:
            target.text = prefix + (target.text or '') + suffix
            return True

    @classmethod
    def focus_tags(cls, element, tags):
        last = None
        marked = []
        buff = 0
        for i, child in enumerate(element):
            cls.focus_tags(child, tags)
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

    @classmethod
    def remove_tags(cls, element, tags):
        if len(tags) == 0:
            return
        last = None
        marked = []
        buff = 0
        remove_all = '*' in tags
        for i, child in enumerate(element):
            cls.remove_tags(child, tags)
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

    @classmethod
    def get_tags(cls, element):
        def aux(element, accu):
            accu.append(element.tag)
            for child in element:
                aux(child, accu)
            return set(accu)
        return aux(element, [])

    @classmethod
    def count_tags(cls, element):
        def aux(element, accu):
            try:
                accu[element.tag] += 1
            except KeyError:
                accu[element.tag] = 1
            for child in element:
                aux(child, accu)
            return accu
        return aux(element, {})

    @classmethod
    def rewrite_tags(cls, element, tags, new_tag):
        if element.tag in tags:
            element.tag = new_tag
        for child in element:
            cls.rewrite_tags(child, tags, new_tag)

    @classmethod
    def rotate_newlines(cls, element):
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
            cls.rotate_newlines(child)

    @classmethod
    def guess_spacing(cls, text):
        if text is None:
            return ''
        m = [''] + re.findall(r"\n(\s*)", text, re.MULTILINE)
        return m[-1]
