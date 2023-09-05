import copy
import os
import pytest

from magpie.xml import XmlEngine
from util import assert_diff


@pytest.fixture
def xml_engine():
    return XmlEngine()

@pytest.fixture
def file_contents():
    file_name = 'Triangle.java'
    path = os.path.join('examples', 'code', 'triangle-java_slow', file_name)
    with open(path, 'r') as myfile:
        return myfile.read()

@pytest.fixture
def engine_contents(xml_engine):
    file_name = 'Triangle.java.xml'
    path = os.path.join('examples', 'code', 'triangle-java_slow', file_name)
    return {file_name: xml_engine.get_contents(path)}

@pytest.fixture
def engine_locations(xml_engine, engine_contents):
    file_name = 'Triangle.java.xml'
    path = os.path.join('examples', 'code', 'triangle-java_slow', file_name)
    contents = xml_engine.get_contents(path)
    return {file_name: xml_engine.get_locations(contents)}

def test_dump(xml_engine, file_contents, engine_contents):
    """Immediate dump should be transparent"""
    file_name = 'Triangle.java.xml'
    dump = xml_engine.dump(engine_contents[file_name])
    assert dump == file_contents

def test_deletion1(xml_engine, engine_contents, engine_locations):
    """Deletion should work"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target = (file_name, 'expr_stmt', 0)
    assert xml_engine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)
    dump = xml_engine.dump(engine_contents[file_name])
    new_dump = xml_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(dump, new_dump, expected)

def test_deletion2(xml_engine, engine_contents, engine_locations):
    """Deletions should only be applied once"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target = (file_name, 'expr_stmt', 0)
    assert xml_engine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)
    assert not xml_engine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target)

def test_replacement1(xml_engine, engine_contents, engine_locations):
    """Identical replacements should not be applied"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'expr_stmt', 3)
    assert not xml_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)

def test_replacement2(xml_engine, engine_contents, engine_locations):
    """Replacement should work"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'expr_stmt', 0)
    target2 = (file_name, 'comment', 0)
    assert not xml_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)
    assert xml_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    dump = xml_engine.dump(engine_contents[file_name])
    new_dump = xml_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        // Sort the sides so that a <= b <= c
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(dump, new_dump, expected)

def test_replacement3(xml_engine, engine_contents, engine_locations):
    """Identical replacements should not be applied (even after replacement)"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'expr_stmt', 0)
    target2 = (file_name, 'comment', 0)
    assert not xml_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target1)
    assert xml_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert not xml_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    dump = xml_engine.dump(engine_contents[file_name])
    new_dump = xml_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        // Sort the sides so that a <= b <= c
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(dump, new_dump, expected)

def test_deletethenreplace(xml_engine, engine_contents, engine_locations):
    """It should be possible to replace something deleted"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'expr_stmt', 0)
    target2 = (file_name, 'comment', 0)
    assert xml_engine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target1)
    assert xml_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    dump = xml_engine.dump(engine_contents[file_name])
    new_dump = xml_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        // Sort the sides so that a <= b <= c
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(dump, new_dump, expected)

def test_replacethendelete(xml_engine, engine_contents, engine_locations):
    """It should be possible to delete something replaced"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, 'expr_stmt', 0)
    target2 = (file_name, 'comment', 0)
    print(new_locations[file_name]['expr_stmt'])
    assert xml_engine.do_replace(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    print(new_locations[file_name]['expr_stmt'])
    assert xml_engine.do_delete(engine_contents, engine_locations, new_contents, new_locations, target1)
    dump = xml_engine.dump(engine_contents[file_name])
    new_dump = xml_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(dump, new_dump, expected)

def test_insertion1(xml_engine, engine_contents, engine_locations):
    """Insertion should work"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_block', 10)
    target2 = (file_name, 'expr_stmt', 1)
    assert xml_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    dump = xml_engine.dump(engine_contents[file_name])
    new_dump = xml_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -7,6 +7,8 @@
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
         delay();
+
+        a = b;
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(dump, new_dump, expected)

def test_insertion2(xml_engine, engine_contents, engine_locations):
    """Insertion should be applied in order"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_block', 10)
    target2 = (file_name, 'expr_stmt', 1)
    target3 = (file_name, 'expr_stmt', 0)
    assert xml_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert xml_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target3)
    dump = xml_engine.dump(engine_contents[file_name])
    new_dump = xml_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -5,6 +5,10 @@
     }
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
+
+        delay();
+
+        a = b;
 
         delay();
 
"""
    assert_diff(dump, new_dump, expected)

def test_insertion3(xml_engine, engine_contents, engine_locations):
    """Insertion locations should be correctly updated"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(engine_contents)
    new_locations = copy.deepcopy(engine_locations)
    target1 = (file_name, '_inter_block', 10)
    target2 = (file_name, 'expr_stmt', 1)
    target3 = (file_name, 'expr_stmt', 0)
    target4 = (file_name, '_inter_block', 9)
    target5 = (file_name, '_inter_block', 11)
    assert xml_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target2)
    assert xml_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target1, target3)
    assert xml_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target4, target2)
    assert xml_engine.do_insert(engine_contents, engine_locations, new_contents, new_locations, target5, target2)
    dump = xml_engine.dump(engine_contents[file_name])
    new_dump = xml_engine.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -6,9 +6,17 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
+        a = b;
+
+        delay();
+
+        a = b;
+
         delay();
 
         // Sort the sides so that a <= b <= c
+
+        a = b;
         if (a > b) {
             int tmp = a;
             a = b;
"""
    assert_diff(dump, new_dump, expected)
