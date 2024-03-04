import ast
import copy

import magpie.core
import magpie.utils


class AstorModel(magpie.core.BasicModel):
    def init_contents(self):
        with open(self.filename) as f:
            self.contents = ast.parse(f.read()+'\n')

        self.locations = {'stmt': [], '_inter_block': []}
        def visit_node(parent_pos, node):
            for attr in ['body', 'orelse', 'finalbody']:
                if hasattr(node, attr):
                    self.locations['_inter_block'].append(parent_pos[:] + [(attr, 0)])
                    for i in range(len(node.__dict__[attr])):
                        self.locations['_inter_block'].append(parent_pos[:] + [(attr, i+1)])
                        current_pos = parent_pos[:] + [(attr, i)]
                        self.locations['stmt'].append(current_pos)
                        visit_node(current_pos, node.__dict__[attr][i])
        visit_node([], self.contents)

    def dump(self):
        return ast.unparse(self.contents)

    def do_replace(self, ref_model, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, tag, path index
        o_f, o_t, o_i = target_orig # file name, tag, path index
        if (d_f != self.filename or
            o_f != ref_model.filename):
            raise ValueError()
        dst_root = self.contents
        dst_pos = self.locations[d_t][d_i]
        ingr_root = ref_model.contents
        ingr_pos = ref_model.locations[o_t][o_i]
        try:
            dst_block, dst_index = self._pos_2_block_n_index(dst_root, dst_pos)
            src_block, src_index = self._pos_2_block_n_index(ingr_root, ingr_pos)
        except IndexError:
            return False
        if ast.dump(dst_block[dst_index]) == ast.dump(src_block[src_index]):
            return False
        dst_block[dst_index] = copy.deepcopy(src_block[src_index])
        return True

    def do_insert(self, ref_model, target_dest, target_orig):
        d_f, d_t, d_i = target_dest # file name, tag, path index
        o_f, o_t, o_i = target_orig # file name, tag, path index
        if (d_f != self.filename or
            o_f != ref_model.filename):
            raise ValueError()
        dst_root = self.contents
        dst_pos = self.locations[d_t][d_i]
        ingr_root = ref_model.contents
        ingr_pos = ref_model.locations[o_t][o_i]
        try:
            dst_block, dst_index = self._pos_2_block_n_index(dst_root, dst_pos)
            src_block, src_index = self._pos_2_block_n_index(ingr_root, ingr_pos)
        except IndexError:
            return False
        dst_block.insert(dst_index, copy.deepcopy(src_block[src_index]))
        depth = len(dst_pos)
        parent = dst_pos[:depth-1]
        index = dst_pos[depth - 1][1]
        for pos in self.locations[o_t]:
            if pos[:depth-1] == parent and len(pos) >= depth and index <= pos[depth-1][1]:
                a, i = pos[depth-1]
                pos[depth-1] = (a, i + 1)
        for pos in self.locations[d_t]:
            if pos[:depth-1] == parent and len(pos) >= depth and index <= pos[depth-1][1]:
                a, i = pos[depth-1]
                pos[depth-1] = (a, i + 1)
        return True

    def do_delete(self, target):
        d_f, d_t, d_i = target # file name, tag, path index
        if d_f != self.filename:
            raise ValueError()
        dst_root = self.contents
        dst_pos = self.locations[d_t][d_i]
        try:
            dst_block, dst_index = self._pos_2_block_n_index(dst_root, dst_pos)
        except IndexError:
            return False
        if isinstance(dst_block[dst_index], ast.Pass):
            return False
        dst_block[dst_index] = ast.Pass()
        return True

    def _pos_2_block_n_index(self, root, pos):
        """
        :param root: The root node of AST
        :type root: :py:class:`ast.AST`
        :param pos: The position of the node in the tree
        :type pos: list(tuple(str, int))
        :return: The node's parent block and the index within the block
        :rtype: tuple(:py:class:`ast.AST`, int)
        """
        node = root
        for i in range(len(pos) - 1):
            block, index = pos[i]
            node = node.__dict__[block][index]
        return (node.__dict__[pos[-1][0]], pos[-1][1])

magpie.utils.known_models.append(AstorModel)
