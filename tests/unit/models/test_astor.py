import copy
import os
import pathlib
import re

import pytest

from magpie.models.astor import AstorModel

from .util import assert_diff


@pytest.fixture
def astor_model():
    model = AstorModel('triangle.py')
    cwd = pathlib.Path.cwd()
    try:
        os.chdir(pathlib.Path('tests') / 'examples')
        model.init_contents()
    finally:
        os.chdir(cwd)
    return model

@pytest.fixture
def file_contents():
    path = pathlib.Path('tests') / 'examples' / 'triangle.py'
    with path.open('r') as myfile:
        return myfile.read()

def test_dump(astor_model, file_contents):
    """Immediate dump should be transparent (as much as possible)"""
    dump = astor_model.dump()
    dump_list = dump.split('\n')
    orig_list = file_contents.split('\n')
    while dump_list or orig_list:
        # skip empty lines
        if dump_list and not dump_list[0]:
            dump_list.pop(0)
            continue
        if orig_list and not orig_list[0]:
            orig_list.pop(0)
            continue
        # skip comment lines
        if orig_list[0].lstrip()[0] == '#':
            orig_list.pop(0)
            continue
        l1, l2 = dump_list.pop(0), orig_list.pop(0)
        # ast.unparse might add new parentheses
        l1 = re.sub(r'[()]', '', l1)
        l2 = re.sub(r'[()]', '', l2)
        assert l1 == l2[:len(l1)]

def test_deletion1(astor_model):
    """Deletion should work"""
    variant = copy.deepcopy(astor_model)
    target = ('triangle.py', 'stmt', 7)
    assert variant.do_delete(target)
    expected = """--- 
+++ 
@@ -8,7 +8,7 @@
     time.sleep(0.01)
 
 def classify_triangle(a, b, c):
-    delay()
+    pass
     if a > b:
         tmp = a
         a = b
"""
    assert_diff(astor_model.dump(), variant.dump(), expected)

def test_deletion2(astor_model):
    """Deletions should only be applied once"""
    variant = copy.deepcopy(astor_model)
    target = ('triangle.py', 'stmt', 7)
    assert variant.do_delete(target)
    assert not variant.do_delete(target)

def test_replacement1(astor_model):
    """Identical replacements should not be applied"""
    variant = copy.deepcopy(astor_model)
    target1 = ('triangle.py', 'stmt', 7)
    assert not variant.do_replace(astor_model, target1, target1)

def test_replacement2(astor_model):
    """Replacement should work"""
    variant = copy.deepcopy(astor_model)
    target1 = ('triangle.py', 'stmt', 7)
    target2 = ('triangle.py', 'stmt', 5)
    assert not variant.do_replace(astor_model, target1, target1)
    assert variant.do_replace(astor_model, target1, target2)
    expected = """--- 
+++ 
@@ -8,7 +8,7 @@
     time.sleep(0.01)
 
 def classify_triangle(a, b, c):
-    delay()
+    time.sleep(0.01)
     if a > b:
         tmp = a
         a = b
"""
    assert_diff(astor_model.dump(), variant.dump(), expected)

def test_replacement3(astor_model):
    """Identical replacements should not be applied (even after replacement)"""
    variant = copy.deepcopy(astor_model)
    target1 = ('triangle.py', 'stmt', 7)
    target2 = ('triangle.py', 'stmt', 5)
    assert not variant.do_replace(astor_model, target1, target1)
    assert variant.do_replace(astor_model, target1, target2)
    assert not variant.do_replace(astor_model, target1, target2)

def test_insertion1(astor_model):
    """Insertion should work"""
    variant = copy.deepcopy(astor_model)
    target1 = ('triangle.py', '_inter_block', 11)
    target2 = ('triangle.py', 'stmt', 5)
    assert variant.do_insert(astor_model, target1, target2)
    expected = """--- 
+++ 
@@ -9,6 +9,7 @@
 
 def classify_triangle(a, b, c):
     delay()
+    time.sleep(0.01)
     if a > b:
         tmp = a
         a = b
"""
    assert_diff(astor_model.dump(), variant.dump(), expected)

def test_insertion2(astor_model):
    """Insertion should be applied in order"""
    variant = copy.deepcopy(astor_model)
    target1 = ('triangle.py', '_inter_block', 11)
    target2 = ('triangle.py', 'stmt', 5)
    target3 = ('triangle.py', 'stmt', 7)
    assert variant.do_insert(astor_model, target1, target2)
    assert variant.do_insert(astor_model, target1, target3)
    expected = """--- 
+++ 
@@ -8,6 +8,8 @@
     time.sleep(0.01)
 
 def classify_triangle(a, b, c):
+    delay()
+    time.sleep(0.01)
     delay()
     if a > b:
         tmp = a
"""
    assert_diff(astor_model.dump(), variant.dump(), expected)

def test_insertion3(astor_model):
    """Insertion locations should be correctly updated"""
    variant = copy.deepcopy(astor_model)
    target1 = ('triangle.py', '_inter_block', 11)
    target2 = ('triangle.py', 'stmt', 5)
    target3 = ('triangle.py', '_inter_block', 10)
    target4 = ('triangle.py', '_inter_block', 12)
    assert variant.do_insert(astor_model, target1, target2)
    assert variant.do_insert(astor_model, target3, target2)
    assert variant.do_insert(astor_model, target1, target2)
    assert variant.do_insert(astor_model, target4, target2)
    expected = """--- 
+++ 
@@ -8,11 +8,15 @@
     time.sleep(0.01)
 
 def classify_triangle(a, b, c):
+    time.sleep(0.01)
     delay()
+    time.sleep(0.01)
+    time.sleep(0.01)
     if a > b:
         tmp = a
         a = b
         b = tmp
+    time.sleep(0.01)
     if a > c:
         tmp = a
         a = c
"""
    assert_diff(astor_model.dump(), variant.dump(), expected)
