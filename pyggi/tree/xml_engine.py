import copy
import re
import os
from . import AbstractTreeEngine
from xml.etree import ElementTree

class XmlEngine(AbstractTreeEngine):
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
    def get_modification_points(cls, contents_of_file):
        def aux(accu, prefix, root):
            tags = dict()
            for child in root:
                if child.tag in tags:
                    tags[child.tag] += 1
                else:
                    tags[child.tag] = 1
                s = '{}/{}[{}]'.format(prefix, child.tag, tags[child.tag])
                accu.append(s)
                accu = aux(accu, s, child)
            return accu
        return aux([], '.', contents_of_file)

    @classmethod
    def get_source(cls, program, file_name, index):
        # never used?
        return cls.dump(program.contents[file_name].find(program.modification_points[file_name][index]))

    @classmethod
    def write_to_tmp_dir(cls, contents_of_file, tmp_path):
        root, ext = os.path.splitext(tmp_path)
        assert ext == '.xml'
        super().write_to_tmp_dir(contents_of_file, root)

    @classmethod
    def reset_in_tmp_dir(cls, target_file, ref_path, tmp_path):
        root, ext = os.path.splitext(target_file)
        assert ext == '.xml'
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
        assert xpath != '.'
        if prefix is None:
            pattern = re.compile(r'^(.*)/([^\[]+)(?:\[([^\]]+)\])?$')
            match = re.match(pattern, xpath)
            assert match
            return (match.group(1), match.group(2), int(match.group(3)), None)
        else:
            if xpath[:len(prefix)+1] == prefix+'/':
                pattern = re.compile(r'^/([^\[]+)(?:\[([^\]]+)\])?(?:/(.*))?$')
                match = re.match(pattern, xpath[len(prefix):])
                assert match
                return (prefix, match.group(1), int(match.group(2)), match.group(3))
            else:
                return (None, None, None, None)

    @classmethod
    def do_replace(cls, program, target_dest, target_orig, new_contents, modification_points):
        # get elements
        target = new_contents[target_dest[0]].find(modification_points[target_dest[0]][target_dest[1]])
        ingredient = program.contents[target_orig[0]].find(program.modification_points[target_orig[0]][target_orig[1]])
        if target is None or ingredient is None:
            return False
        if target == ingredient:
            return True

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
            head, tag, pos, _ = cls.split_xpath(modification_points[target_dest[0]][target_dest[1]])
            itag = 1
            for i, xpath in enumerate(modification_points[target_dest[0]]):
                h, t, p, s = cls.split_xpath(xpath, head)
                if i < target_dest[1]:
                    if h != head:
                        continue
                    elif t == ingredient.tag:
                        itag += 1
                elif i == target_dest[1]:
                    modification_points[target_dest[0]][i] = '{}/{}[{}]'.format(h, ingredient.tag, itag)
                elif h != head:
                    break
                elif t == tag:
                    if p == pos:
                        new_pos = 'deleted'
                    elif s:
                        new_pos = '{}/{}[{}]/{}'.format(h, t, p-1, s)
                    else:
                        new_pos = '{}/{}[{}]'.format(h, t, p-1)
                    modification_points[target_dest[0]][i] = new_pos
                elif t == ingredient.tag:
                    if s:
                        new_pos = '{}/{}[{}]/{}'.format(h, t, p+1, s)
                    else:
                        new_pos = '{}/{}[{}]'.format(h, t, p+1)
                    modification_points[target_dest[0]][i] = new_pos
        return True

    @classmethod
    def do_insert(cls, program, target_dest, target_orig, direction, new_contents, modification_points):
        # get elements
        target = new_contents[target_dest[0]].find(modification_points[target_dest[0]][target_dest[1]])
        parent = new_contents[target_dest[0]].find(modification_points[target_dest[0]][target_dest[1]]+'..')
        ingredient = program.contents[target_orig[0]].find(program.modification_points[target_orig[0]][target_orig[1]])
        if target is None or ingredient is None:
            return False

        # mutate
        sp = cls.guess_spacing(parent.text)
        for i, child in enumerate(parent):
            if child == target:
                tmp = copy.deepcopy(ingredient)
                if direction == 'after':
                    tmp.tail = child.tail
                    child.tail = '\n' + sp
                    i += 1
                else:
                    tmp.tail = '\n' + sp
                parent.insert(i, tmp)
                break
            sp = cls.guess_spacing(child.tail)
        else:
            assert False

        # update modification points
        head, tag, pos, _ = cls.split_xpath(modification_points[target_dest[0]][target_dest[1]])
        for i, xpath in enumerate(modification_points[target_dest[0]]):
            if i < target_dest[1]:
                continue
            h, t, p, s = cls.split_xpath(xpath, head)
            if h != head and xpath != 'deleted':
                break
            if t == tag and p == pos and direction == 'after':
                continue
            if t in [ingredient.tag, tag]:
                if s:
                    new_pos = '{}/{}[{}]/{}'.format(h, t, p+1, s)
                else:
                    new_pos = '{}/{}[{}]'.format(h, t, p+1)
                modification_points[target_dest[0]][i] = new_pos
        return True

    @classmethod
    def do_delete(cls, program, target, new_contents, modification_points):
        # get elements
        target = new_contents[target[0]].find(modification_points[target[0]][target[1]])
        if target is None:
            return False

        # mutate
        old_tag = target.tag
        old_tail = target.tail
        target.clear() # to remove children
        target.tag = old_tag
        target.tail = old_tail
        return True

    @classmethod
    def do_set_text(cls, program, target, value, new_contents, modification_points):
        target = new_contents[target[0]].find(modification_points[target[0]][target[1]])
        if target is None:
            return False
        target.text = value
        return True

    @classmethod
    def do_wrap_text(cls, program, target, prefix, suffix, new_contents, modification_points):
        target = new_contents[target[0]].find(modification_points[target[0]][target[1]])
        if target is None:
            return False
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
