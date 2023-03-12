import copy
import os
import pytest

from magpie.line import LineEngine
from util import assert_diff


@pytest.fixture
def line_engine():
    return LineEngine()

@pytest.fixture
def file_contents():
    file_name = 'triangle.py'
    path = os.path.join('examples', 'code', 'triangle-py_slow', file_name)
    with open(path, 'r') as myfile:
        return myfile.read()

@pytest.fixture
def engine_contents(line_engine):
    file_name = 'triangle.py'
    path = os.path.join('examples', 'code', 'triangle-py_slow', file_name)
    return {file_name: line_engine.get_contents(path)}

@pytest.fixture
def engine_locations(line_engine, engine_contents):
    file_name = 'triangle.py'
    path = os.path.join('examples', 'code', 'triangle-py_slow', file_name)
    contents = line_engine.get_contents(path)
    return {file_name: line_engine.get_locations(contents)}

def test_interlines(engine_locations):
    """There should be one more interline"""
    file_name = 'triangle.py'
    assert len(engine_locations[file_name]['_inter_line']) == len(engine_locations[file_name]['line'])+1

def test_dump(line_engine, file_contents, engine_contents):
    """Immediate dump should be transparent"""
    file_name = 'triangle.py'
    dump = line_engine.dump(engine_contents[file_name])
    assert dump == file_contents

def test_deletion1(line_engine, engine_contents, engine_locations):
    """Deletion should work"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target = (file_name, 'line', 14)
    assert line_engine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)
    dump = line_engine.dump(engine_contents[file_name])
    new_dump = line_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -12,7 +12,6 @@
 
 def classify_triangle(a, b, c):
 
-    delay()
 
     # Sort the sides so that a <= b <= c
     if a > b:
"""
    assert_diff(dump, new_dump, expected)

def test_deletion2(line_engine, engine_contents, engine_locations):
    """Deletions should only be applied once"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target = (file_name, 'line', 14)
    assert line_engine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)
    assert not line_engine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)

def test_replacement1(line_engine, engine_contents, engine_locations):
    """Identical replacements should not be applied"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'line', 14)
    assert not line_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)

def test_replacement2(line_engine, engine_contents, engine_locations):
    """Replacement should work"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'line', 14)
    target2 = (file_name, 'line', 15)
    assert not line_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)
    assert line_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    dump = line_engine.dump(engine_contents[file_name])
    new_dump = line_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -12,7 +12,7 @@
 
 def classify_triangle(a, b, c):
 
-    delay()
+
 
     # Sort the sides so that a <= b <= c
     if a > b:
"""
    assert_diff(dump, new_dump, expected)

def test_replacement3(line_engine, engine_contents, engine_locations):
    """Identical replacements should not be applied (even after replacement)"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'line', 14)
    target2 = (file_name, 'line', 15)
    assert not line_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)
    assert line_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert not line_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)

def test_insertion1(line_engine, engine_contents, engine_locations):
    """Insertion should work"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_line', 15)
    target2 = (file_name, 'line', 9)
    assert line_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    dump = line_engine.dump(engine_contents[file_name])
    new_dump = line_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -13,6 +13,7 @@
 def classify_triangle(a, b, c):
 
     delay()
+    time.sleep(0.001)
 
     # Sort the sides so that a <= b <= c
     if a > b:
"""
    assert_diff(dump, new_dump, expected)

def test_insertion2(line_engine, engine_contents, engine_locations):
    """Insertion should be applied in order"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_line', 15)
    target2 = (file_name, 'line', 9)
    target3 = (file_name, 'line', 14)
    assert line_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert line_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target3)
    dump = line_engine.dump(engine_contents[file_name])
    new_dump = line_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -12,6 +12,8 @@
 
 def classify_triangle(a, b, c):
 
+    delay()
+    time.sleep(0.001)
     delay()
 
     # Sort the sides so that a <= b <= c
"""
    assert_diff(dump, new_dump, expected)

def test_insertion3(line_engine, engine_contents, engine_locations):
    """Insertion locations should be correctly updated"""
    file_name = 'triangle.py'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_line', 15)
    target2 = (file_name, 'line', 9)
    target3 = (file_name, 'line', 14)
    target4 = (file_name, '_inter_line', 13)
    target5 = (file_name, '_inter_line', 17)
    assert line_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert line_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target3)
    assert line_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target4, target2)
    assert line_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target5, target2)
    dump = line_engine.dump(engine_contents[file_name])
    new_dump = line_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -11,10 +11,14 @@
 
 
 def classify_triangle(a, b, c):
+    time.sleep(0.001)
 
+    delay()
+    time.sleep(0.001)
     delay()
 
     # Sort the sides so that a <= b <= c
+    time.sleep(0.001)
     if a > b:
         tmp = a
         a = b
"""
    assert_diff(dump, new_dump, expected)
