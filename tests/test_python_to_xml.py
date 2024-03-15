import ast
import pathlib

import pytest

from magpie.models.xml import XmlModel
from magpie.scripts.python_to_xml import read_file_or_stdin, unparse_xml


@pytest.mark.parametrize('filename', pathlib.Path('magpie').glob('**/*.py'))
# @pytest.mark.parametrize('filename', glob.glob('/usr/lib/python3.11/**/*.py', recursive=True))
def test_on_file(filename):
    contents = read_file_or_stdin(filename)
    root = ast.parse(contents+'\n')

    oracle = ast.unparse(root)
    oracle = ast.unparse(ast.parse(oracle, filename='oracle')) # ensures oracle is not buggy

    output = unparse_xml(root, filename)
    naked = XmlModel.strip_xml_from_tree(XmlModel.string_to_tree(output))
    roundtrip = ast.unparse(ast.parse(naked, filename='roundtrip'))
    assert roundtrip == oracle
