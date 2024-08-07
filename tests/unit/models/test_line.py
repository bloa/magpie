import copy
import os
import pathlib

import pytest

from magpie.models.line import LineModel

from .util import assert_diff


@pytest.fixture
def line_model():
    model = LineModel('triangle.py')
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

def test_interlines(line_model):
    """There should be one more interline"""
    assert len(line_model.locations['_inter_line']) == len(line_model.locations['line']) + 1

def test_dump(line_model, file_contents):
    """Immediate dump should be transparent"""
    dump = line_model.dump()
    assert dump == file_contents

def test_deletion1(line_model):
    """Deletion should work"""
    variant = copy.deepcopy(line_model)
    target = ('triangle.py', 'line', 14)
    assert variant.do_delete(target)
    expected = """--- 
+++ 
@@ -12,7 +12,6 @@
 
 def classify_triangle(a, b, c):
     # slow down execution
-    delay()
 
     # sort the sides so that a <= b <= c
     if a > b:
"""
    assert_diff(line_model.dump(), variant.dump(), expected)

def test_deletion2(line_model):
    """Deletions should only be applied once"""
    variant = copy.deepcopy(line_model)
    target = ('triangle.py', 'line', 14)
    assert variant.do_delete(target)
    assert not variant.do_delete(target)

def test_replacement1(line_model):
    """Identical replacements should not be applied"""
    variant = copy.deepcopy(line_model)
    target1 = ('triangle.py', 'line', 14)
    assert not variant.do_replace(line_model, target1, target1)

def test_replacement2(line_model):
    """Replacement should work"""
    variant = copy.deepcopy(line_model)
    target1 = ('triangle.py', 'line', 14)
    target2 = ('triangle.py', 'line', 15)
    assert not variant.do_replace(line_model, target1, target1)
    assert variant.do_replace(line_model, target1, target2)
    expected = """--- 
+++ 
@@ -12,7 +12,7 @@
 
 def classify_triangle(a, b, c):
     # slow down execution
-    delay()
+
 
     # sort the sides so that a <= b <= c
     if a > b:
"""
    assert_diff(line_model.dump(), variant.dump(), expected)

def test_replacement3(line_model):
    """Identical replacements should not be applied (even after replacement)"""
    variant = copy.deepcopy(line_model)
    target1 = ('triangle.py', 'line', 14)
    target2 = ('triangle.py', 'line', 15)
    assert not variant.do_replace(line_model, target1, target1)
    assert variant.do_replace(line_model, target1, target2)
    assert not variant.do_replace(line_model, target1, target2)

def test_insertion1(line_model):
    """Insertion should work"""
    variant = copy.deepcopy(line_model)
    target1 = ('triangle.py', '_inter_line', 15)
    target2 = ('triangle.py', 'line', 9)
    assert variant.do_insert(line_model, target1, target2)
    expected = """--- 
+++ 
@@ -13,6 +13,7 @@
 def classify_triangle(a, b, c):
     # slow down execution
     delay()
+    time.sleep(0.01)
 
     # sort the sides so that a <= b <= c
     if a > b:
"""
    assert_diff(line_model.dump(), variant.dump(), expected)

def test_insertion2(line_model):
    """Insertion should be applied in order"""
    variant = copy.deepcopy(line_model)
    target1 = ('triangle.py', '_inter_line', 15)
    target2 = ('triangle.py', 'line', 9)
    target3 = ('triangle.py', 'line', 14)
    assert variant.do_insert(line_model, target1, target2)
    assert variant.do_insert(line_model, target1, target3)
    expected = """--- 
+++ 
@@ -12,6 +12,8 @@
 
 def classify_triangle(a, b, c):
     # slow down execution
+    delay()
+    time.sleep(0.01)
     delay()
 
     # sort the sides so that a <= b <= c
"""
    assert_diff(line_model.dump(), variant.dump(), expected)

def test_insertion3(line_model):
    """Insertion locations should be correctly updated"""
    variant = copy.deepcopy(line_model)
    target1 = ('triangle.py', '_inter_line', 15)
    target2 = ('triangle.py', 'line', 9)
    target3 = ('triangle.py', '_inter_line', 14)
    target4 = ('triangle.py', '_inter_line', 16)
    assert variant.do_insert(line_model, target1, target2)
    assert variant.do_insert(line_model, target3, target2)
    assert variant.do_insert(line_model, target1, target2)
    assert variant.do_insert(line_model, target4, target2)
    expected = """--- 
+++ 
@@ -12,8 +12,12 @@
 
 def classify_triangle(a, b, c):
     # slow down execution
+    time.sleep(0.01)
     delay()
+    time.sleep(0.01)
+    time.sleep(0.01)
 
+    time.sleep(0.01)
     # sort the sides so that a <= b <= c
     if a > b:
         tmp = a
"""
    assert_diff(line_model.dump(), variant.dump(), expected)
