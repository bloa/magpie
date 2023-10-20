import ast
import copy

from ..base import AbstractEngine


class AstorEngine(AbstractEngine):
    @classmethod
    def get_contents(cls, file_path):
        with open(file_path) as f:
            return ast.parse(f.read()+'\n')

    @classmethod
    def get_locations(cls, root):
        stmts = []
        inter = []
        def visit_node(parent_pos, node):
            for attr in ['body', 'orelse', 'finalbody']:
                if hasattr(node, attr):
                    inter.append(parent_pos[:] + [(attr, 0)])
                    for i in range(len(node.__dict__[attr])):
                        inter.append(parent_pos[:] + [(attr, i+1)])
                        current_pos = parent_pos[:] + [(attr, i)]
                        stmts.append(current_pos)
                        visit_node(current_pos, node.__dict__[attr][i])
        visit_node([], root)
        return {'stmt': stmts, '_inter_block': inter}

    @classmethod
    def dump(cls, contents_of_file):
        return ast.unparse(contents_of_file)

    @classmethod
    def do_replace(cls, contents, locations, new_contents, new_locations, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, tag, path index
        o_f, o_t, o_i = target_orig # file name, tag, path index
        dst_root = new_contents[d_f]
        dst_pos = new_locations[d_f][d_t][d_i]
        ingr_root = contents[o_f]
        ingr_pos = locations[o_f][o_t][o_i]
        if cls.is_valid_pos(dst_root, dst_pos) and cls.is_valid_pos(ingr_root, ingr_pos):
            dst_block, dst_index = cls.pos_2_block_n_index(dst_root, dst_pos)
            src_block, src_index = cls.pos_2_block_n_index(ingr_root, ingr_pos)
            if ast.dump(dst_block[dst_index]) == ast.dump(src_block[src_index]):
                return False
            else:
                dst_block[dst_index] = copy.deepcopy(src_block[src_index])
                return True
        else:
            return False

    @classmethod
    def do_insert(cls, contents, locations, new_contents, new_locations, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, tag, path index
        o_f, o_t, o_i = target_orig # file name, tag, path index
        dst_root = new_contents[d_f]
        dst_pos = new_locations[d_f][d_t][d_i]
        ingr_root = contents[o_f]
        ingr_pos = locations[o_f][o_t][o_i]
        if cls.is_valid_pos(dst_root, dst_pos[:-1]) and cls.is_valid_pos(ingr_root, ingr_pos):
            dst_block, dst_index = cls.pos_2_block_n_index(dst_root, dst_pos)
            src_block, src_index = cls.pos_2_block_n_index(ingr_root, ingr_pos)
            dst_block.insert(dst_index, copy.deepcopy(src_block[src_index]))
            depth = len(dst_pos)
            parent = dst_pos[:depth-1]
            index = dst_pos[depth - 1][1]
            for pos in new_locations[d_f][o_t]:
                if pos[:depth-1] == parent and len(pos) >= depth and index <= pos[depth-1][1]:
                    a, i = pos[depth-1]
                    pos[depth-1] = (a, i + 1)
            for pos in new_locations[d_f][d_t]:
                if pos[:depth-1] == parent and len(pos) >= depth and index <= pos[depth-1][1]:
                    a, i = pos[depth-1]
                    pos[depth-1] = (a, i + 1)
            return True
        else:
            return False

    @classmethod
    def do_delete(cls, contents, locations, new_contents, new_locations, target):
        d_f, d_t, d_i = target # file name, tag, path index
        dst_root = new_contents[d_f]
        dst_pos = new_locations[d_f][d_t][d_i]
        if cls.is_valid_pos(dst_root, dst_pos):
            dst_block, dst_index = cls.pos_2_block_n_index(dst_root, dst_pos)
            if isinstance(dst_block[dst_index], ast.Pass):
                return False
            else:
                dst_block[dst_index] = ast.Pass()
                return True
        else:
            return False

    @classmethod
    def is_pos_type(cls, pos):
        """
        :param pos: The position of the node
        :type pos: ?
        :return: whether it is type of tuple(str, list(tuple(str, int))) and all integers >= 0
        :rtype: bool
        """
        if not isinstance(pos, list):
            return False
        return all(isinstance(t, tuple) and isinstance(t[0], str)
            and isinstance(t[1], int) and t[1] >= 0 for t in pos)

    @classmethod
    def is_valid_pos(cls, root, pos):
        """
        :param root: The root node of AST
        :type root: :py:class:`ast.AST`
        :param pos: The position of the node in the tree
        :type pos: list(tuple(str, int))
        :return: valid or not(i.e., node exists in the tree or not)
        :rtype: bool
        """
        node = root
        for block, index in pos:
            if not block in ['body', 'orelse', 'finalbody']:
                return False
            if not block in node.__dict__:
                return False
            if not index < len(node.__dict__[block]):
                return False
            node = node.__dict__[block][index]
        return True

    @classmethod
    def pos_2_block_n_index(cls, root, pos):
        """
        :param root: The root node of AST
        :type root: :py:class:`ast.AST`
        :param pos: The position of the node in the tree
        :type pos: list(tuple(str, int))
        :return: The node's parent block and the index within the block
        :rtype: tuple(:py:class:`ast.AST`, int)
        """
        return (cls.pos_2_block(root, pos), pos[-1][1])

    @classmethod
    def pos_2_block(cls, root, pos):
        node = root
        for i in range(len(pos) - 1):
            block, index = pos[i]
            node = node.__dict__[block][index]
        return node.__dict__[pos[-1][0]]
