import copy
import os
import pytest
import re

import magpie

from magpie.astor import AstorEngine
from .util import assert_diff

@pytest.fixture
def file_contents():
    file_name = 'triangle.py'
    path = os.path.join('examples', 'code', 'triangle-py_slow', file_name)
    with open(path, 'r') as myfile:
        return myfile.read()

@pytest.fixture
def engine_contents():
    file_name = 'triangle.py'
    path = os.path.join('examples', 'code', 'triangle-py_slow', file_name)
    return {file_name: AstorEngine.get_contents(path)}

@pytest.fixture
def engine_locations(engine_contents):
    file_name = 'triangle.py'
    path = os.path.join('examples', 'code', 'triangle-py_slow', file_name)
    contents = AstorEngine.get_contents(path)
    return {file_name: AstorEngine.get_locations(contents)}

def test_dump(file_contents, engine_contents):
    """Immediate dump should be transparent (as much as possible)"""
    file_name = 'triangle.py'
    dump = AstorEngine.dump(engine_contents[file_name])
    dump_list = dump.split("\n")
    orig_list = file_contents.split("\n")
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

def test_deletion1(engine_contents, engine_locations):
    """Deletion should work"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target = (file_name, 'stmt', 7)
    assert AstorEngine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)
    dump = AstorEngine.dump(engine_contents[file_name])
    new_dump = AstorEngine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -8,7 +8,7 @@
     time.sleep(0.001)
 
 def classify_triangle(a, b, c):
-    delay()
+    pass
     if a > b:
         tmp = a
         a = b
"""
    assert_diff(dump, new_dump, expected)

def test_deletion2(engine_contents, engine_locations):
    """Deletions should only be applied once"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target = (file_name, 'stmt', 7)
    assert AstorEngine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)
    assert not AstorEngine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)

def test_replacement1(engine_contents, engine_locations):
    """Identical replacements should not be applied"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'stmt', 7)
    assert not AstorEngine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)

def test_replacement2(engine_contents, engine_locations):
    """Replacement should work"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'stmt', 7)
    target2 = (file_name, 'stmt', 5)
    assert not AstorEngine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)
    assert AstorEngine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    dump = AstorEngine.dump(engine_contents[file_name])
    new_dump = AstorEngine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -8,7 +8,7 @@
     time.sleep(0.001)
 
 def classify_triangle(a, b, c):
-    delay()
+    time.sleep(0.001)
     if a > b:
         tmp = a
         a = b
"""
    assert_diff(dump, new_dump, expected)

def test_replacement3(engine_contents, engine_locations):
    """Identical replacements should not be applied (even after replacement)"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'stmt', 7)
    target2 = (file_name, 'stmt', 5)
    assert not AstorEngine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)
    assert AstorEngine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert not AstorEngine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)

def test_insertion1(engine_contents, engine_locations):
    """Insertion should work"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_block', 11)
    target2 = (file_name, 'stmt', 5)
    assert AstorEngine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    dump = AstorEngine.dump(engine_contents[file_name])
    new_dump = AstorEngine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -9,6 +9,7 @@
 
 def classify_triangle(a, b, c):
     delay()
+    time.sleep(0.001)
     if a > b:
         tmp = a
         a = b
"""
    assert_diff(dump, new_dump, expected)

def test_insertion2(engine_contents, engine_locations):
    """Insertion should be applied in order"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_block', 11)
    target2 = (file_name, 'stmt', 5)
    target3 = (file_name, 'stmt', 7)
    assert AstorEngine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert AstorEngine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target3)
    dump = AstorEngine.dump(engine_contents[file_name])
    new_dump = AstorEngine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -8,6 +8,8 @@
     time.sleep(0.001)
 
 def classify_triangle(a, b, c):
+    delay()
+    time.sleep(0.001)
     delay()
     if a > b:
         tmp = a
"""
    assert_diff(dump, new_dump, expected)

def test_insertion3(engine_contents, engine_locations):
    """Insertion locations should be correctly updated"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_block', 11)
    target2 = (file_name, 'stmt', 5)
    target3 = (file_name, 'stmt', 7)
    target4 = (file_name, '_inter_block', 10)
    target5 = (file_name, '_inter_block', 12)
    assert AstorEngine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert AstorEngine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target3)
    assert AstorEngine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target4, target2)
    assert AstorEngine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target5, target2)
    dump = AstorEngine.dump(engine_contents[file_name])
    new_dump = AstorEngine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -8,11 +8,15 @@
     time.sleep(0.001)
 
 def classify_triangle(a, b, c):
+    time.sleep(0.001)
+    delay()
+    time.sleep(0.001)
     delay()
     if a > b:
         tmp = a
         a = b
         b = tmp
+    time.sleep(0.001)
     if a > c:
         tmp = a
         a = c
"""
    assert_diff(dump, new_dump, expected)
