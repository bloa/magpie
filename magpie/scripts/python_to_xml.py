import argparse
import ast
import pathlib
import sys
from contextlib import contextmanager


def read_file_or_stdin(filename):
    if filename == 'stdin':
        return sys.stdin.read()
    with pathlib.Path(filename).open('r') as f:
        return f.read()

def unparse_xml(root, filename=''):
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<unit filename="{filename}">
{XmlUnparser().visit(root)}
</unit>
"""


# mostly lifted from cpython/Lib/ast.py
# see https://docs.python.org/3/library/ast.html#abstract-grammar
class XmlUnparser(ast._Unparser):

    @contextmanager
    def add_xml(self, tag):
        """A context manager for xml tags."""
        with self.buffered(self._source[:]) as buffer:
            index = len(buffer)
            yield
        if buffer:
            while index < len(buffer) and not buffer[index].lstrip():
                self.write_raw(buffer[index])
                index += 1
            self.write_raw(f'<{tag}>')
            self.write_raw(*buffer[index:])
            self.write_raw(f'</{tag}>')

    def write(self, *text):
        """Add new source parts, sanitize for XML"""
        def sanitize_xml(s):
            if not isinstance(s, str):
                return s
            return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        super().write(*[sanitize_xml(s) for s in text])

    def write_raw(self, *text):
        """Add new source parts, but unsanitized"""
        super().write(*text)

    def fill(self, text=''):
        """Indent a piece of text and append it, according to the current indentation level"""
        super().fill()
        self.write(text)

    def traverse(self, node):
        if isinstance(node, ast.stmt):
            with self.add_xml('stmt'):
                with self.add_xml(node.__class__.__name__):
                    super().traverse(node)
        elif isinstance(node, ast.expr):
            with self.add_xml('expr'):
                with self.add_xml(node.__class__.__name__):
                    super().traverse(node)
        elif isinstance(node, ast.operator):
            with self.add_xml('operator'):
                with self.add_xml(node.__class__.__name__):
                    super().traverse(node)
        elif isinstance(node, ast.AST):
            with self.add_xml(node.__class__.__name__):
                super().traverse(node)
        else:
            super().traverse(node)

    @contextmanager
    def block(self, *, extra = None):
        """A context manager for preparing the source for blocks. It adds
        the character':', increases the indentation on enter and decreases
        the indentation on exit. If *extra* is given, it will be directly
        appended after the colon character.
        """
        self.write(':')
        if extra:
            self.write(extra)
        self._indent += 1
        with self.add_xml('block'):
            yield
        self._indent -= 1

    def visit_Module(self, node):
        with self.add_xml('block'):
            super().visit_Module(node)

    def visit_If(self, node):
        self.fill('if ')
        self.traverse(node.test)
        with self.block():
            self.traverse(node.body)
        # # collapse nested ifs into equivalent elifs.
        # if node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], If):
        #     node = node.orelse[0]
        #     self.fill("elif ")
        #     self.traverse(node.test)
        #     with self.block():
        #         self.traverse(node.body)
        # final else
        if node.orelse:
            self.fill('else')
            with self.block():
                self.traverse(node.orelse)

    def visit_Compare(self, node):
        with self.require_parens(ast._Precedence.CMP, node):
            self.set_precedence(ast._Precedence.CMP.next(), node.left, *node.comparators)
            self.traverse(node.left)
            for o, e in zip(node.ops, node.comparators):
                self.write(' ')
                with self.add_xml('cmpop'):
                    self.write(self.cmpops[o.__class__.__name__])
                self.write(' ')
                self.traverse(e)

    def visit_UnaryOp(self, node):
        operator = self.unop[node.op.__class__.__name__]
        operator_precedence = self.unop_precedence[operator]
        with self.require_parens(operator_precedence, node):
            with self.add_xml(node.op.__class__.__name__.lower()):
                self.write(operator)
            # factor prefixes (+, -, ~) shouldn't be separated
            # from the value they belong, (e.g: +1 instead of + 1)
            if operator_precedence is not ast._Precedence.FACTOR:
                self.write(' ')
            self.set_precedence(operator_precedence, node.operand)
            self.traverse(node.operand)

    binop_rassoc = frozenset(('**',))
    def visit_BinOp(self, node):
        operator = self.binop[node.op.__class__.__name__]
        operator_precedence = self.binop_precedence[operator]
        with self.require_parens(operator_precedence, node):
            if operator in self.binop_rassoc:
                left_precedence = operator_precedence.next()
                right_precedence = operator_precedence
            else:
                left_precedence = operator_precedence
                right_precedence = operator_precedence.next()

            self.set_precedence(left_precedence, node.left)
            self.traverse(node.left)
            self.write(' ')
            with self.add_xml(node.op.__class__.__name__.lower()):
                self.write(operator)
            self.write(' ')
            self.set_precedence(right_precedence, node.right)
            self.traverse(node.right)

    def visit_BoolOp(self, node):
        operator = self.boolops[node.op.__class__.__name__]
        operator_precedence = self.boolop_precedence[operator]

        def increasing_level_traverse(node):
            nonlocal operator_precedence
            operator_precedence = operator_precedence.next()
            self.set_precedence(operator_precedence, node)
            self.traverse(node)

        with self.require_parens(operator_precedence, node):
            def tmp():
                self.write(' ')
                with self.add_xml('boolop'):
                    self.write(operator)
                self.write(' ')
            self.interleave(tmp, increasing_level_traverse, node.values)

    def visit_JoinedStr(self, node):
        self.write('f')

        fstring_parts = []
        for value in node.values:
            with self.buffered() as buffer:
                self._write_fstring_inner(value)
            fstring_parts.append(
                (''.join(buffer), isinstance(value, ast.Constant)),
            )

        new_fstring_parts = []
        quote_types = list(ast._ALL_QUOTES)
        fallback_to_repr = False
        for value, is_constant in fstring_parts:
            if is_constant:
                value, new_quote_types = self._str_literal_helper(
                    value,
                    quote_types=quote_types,
                    escape_special_whitespace=True,
                )
                if set(new_quote_types).isdisjoint(quote_types):
                    fallback_to_repr = True
                    break
                quote_types = new_quote_types
            else:
                if "\n" in value:
                    quote_types = [q for q in quote_types if q in ast._MULTI_QUOTES]
                    assert quote_types

                new_quote_types = [q for q in quote_types if q not in value]
                if new_quote_types:
                    quote_types = new_quote_types
            new_fstring_parts.append(value)

        if fallback_to_repr:
            # If we weren't able to find a quote type that works for all parts
            # of the JoinedStr, fallback to using repr and triple single quotes.
            quote_types = ["'''"]
            new_fstring_parts.clear()
            for value, is_constant in fstring_parts:
                if is_constant:
                    value = repr('"' + value)  # force repr to use single quotes
                    expected_prefix = "'\""
                    assert value.startswith(expected_prefix), repr(value)
                    value = value[len(expected_prefix):-1]
                new_fstring_parts.append(value)

        value = ''.join(new_fstring_parts)
        quote_type = quote_types[0]
        self.write_raw(f'{quote_type}{value}{quote_type}')

    def visit_FormattedValue(self, node):
        def unparse_inner(inner):
            unparser = type(self)()
            unparser.set_precedence(ast._Precedence.TEST.next(), inner)
            return unparser.visit(inner)

        with self.delimit('{', '}'):
            expr = unparse_inner(node.value)
            if expr.startswith('{'):
                # Separate pair of opening brackets as "{ {"
                self.write(' ')
            self.write_raw(expr)
            if node.conversion != -1:
                self.write(f'!{chr(node.conversion)}')
            if node.format_spec:
                self.write(':')
                self._write_fstring_inner(node.format_spec, is_format_spec=True)

    def visit_Lambda(self, node):
        with self.require_parens(ast._Precedence.TEST, node):
            self.write('lambda')
            with self.buffered() as buffer:
                self.traverse(node.args)
            if buffer:
                self.write(' ')
                self.write_raw(*buffer)
            self.write(': ')
            self.set_precedence(ast._Precedence.TEST, node.body)
            self.traverse(node.body)


# ================================================================================
# Main function
# ================================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie Python to XML formatter')
    parser.add_argument('file', default='stdin', nargs='?')
    args = parser.parse_args()

    contents = read_file_or_stdin(args.file)
    root = ast.parse(contents+'\n')
    print(unparse_xml(root, args.file))
