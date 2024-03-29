import ast
import glob

import pytest

from clear_xml import strip_xml_from_tree, string_to_tree
from python_to_xml import read_file_or_stdin, unparse_xml


@pytest.mark.parametrize('filename', glob.glob('magpie/**/*.py', recursive=True))
# @pytest.mark.parametrize('filename', glob.glob('/usr/lib/python3.11/**/*.py', recursive=True))
def test_on_file(filename):
    contents = read_file_or_stdin(filename)
    root = ast.parse(contents+'\n')

    oracle = ast.unparse(root)
    oracle = ast.unparse(ast.parse(oracle, filename='oracle')) # ensures oracle is not buggy

    output = unparse_xml(root, filename)
    naked = strip_xml_from_tree(string_to_tree(output))
    roundtrip = ast.unparse(ast.parse(naked, filename='roundtrip'))
    assert roundtrip == oracle
