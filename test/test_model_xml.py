import copy
import os
import pytest

from magpie.xml import XmlModel
from .util import assert_diff


@pytest.fixture
def xml_model():
    return XmlModel()

@pytest.fixture
def file_contents():
    file_name = 'Triangle.java'
    path = os.path.join('examples', 'code', 'triangle-java_slow', file_name)
    with open(path, 'r') as myfile:
        return myfile.read()

@pytest.fixture
def model_contents(xml_model):
    file_name = 'Triangle.java.xml'
    path = os.path.join('examples', 'code', 'triangle-java_slow', file_name)
    return {file_name: xml_model.get_contents(path)}

@pytest.fixture
def model_locations(xml_model, model_contents):
    file_name = 'Triangle.java.xml'
    path = os.path.join('examples', 'code', 'triangle-java_slow', file_name)
    contents = xml_model.get_contents(path)
    return {file_name: xml_model.get_locations(contents)}

def test_dump(xml_model, file_contents, model_contents):
    """Immediate dump should be transparent"""
    file_name = 'Triangle.java.xml'
    dump = xml_model.dump(model_contents[file_name])
    assert dump == file_contents

def test_deletion1(xml_model, model_contents, model_locations):
    """Deletion should work"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target = (file_name, 'expr_stmt', 0)
    assert xml_model.do_delete(model_contents, model_locations, new_contents, new_locations, target)
    dump = xml_model.dump(model_contents[file_name])
    new_dump = xml_model.dump(new_contents[file_name])
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

def test_deletion2(xml_model, model_contents, model_locations):
    """Deletions should only be applied once"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target = (file_name, 'expr_stmt', 0)
    assert xml_model.do_delete(model_contents, model_locations, new_contents, new_locations, target)
    assert not xml_model.do_delete(model_contents, model_locations, new_contents, new_locations, target)

def test_replacement1(xml_model, model_contents, model_locations):
    """Identical replacements should not be applied"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target1 = (file_name, 'expr_stmt', 3)
    assert not xml_model.do_replace(model_contents, model_locations, new_contents, new_locations, target1, target1)

def test_replacement2(xml_model, model_contents, model_locations):
    """Replacement should work"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target1 = (file_name, 'expr_stmt', 0)
    target2 = (file_name, 'comment', 0)
    assert not xml_model.do_replace(model_contents, model_locations, new_contents, new_locations, target1, target1)
    assert xml_model.do_replace(model_contents, model_locations, new_contents, new_locations, target1, target2)
    dump = xml_model.dump(model_contents[file_name])
    new_dump = xml_model.dump(new_contents[file_name])
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

def test_replacement3(xml_model, model_contents, model_locations):
    """Identical replacements should not be applied (even after replacement)"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target1 = (file_name, 'expr_stmt', 0)
    target2 = (file_name, 'comment', 0)
    assert not xml_model.do_replace(model_contents, model_locations, new_contents, new_locations, target1, target1)
    assert xml_model.do_replace(model_contents, model_locations, new_contents, new_locations, target1, target2)
    assert not xml_model.do_replace(model_contents, model_locations, new_contents, new_locations, target1, target2)
    dump = xml_model.dump(model_contents[file_name])
    new_dump = xml_model.dump(new_contents[file_name])
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

def test_deletethenreplace(xml_model, model_contents, model_locations):
    """It should be possible to replace something deleted"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target1 = (file_name, 'expr_stmt', 0)
    target2 = (file_name, 'comment', 0)
    assert xml_model.do_delete(model_contents, model_locations, new_contents, new_locations, target1)
    assert xml_model.do_replace(model_contents, model_locations, new_contents, new_locations, target1, target2)
    dump = xml_model.dump(model_contents[file_name])
    new_dump = xml_model.dump(new_contents[file_name])
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

def test_replacethendelete(xml_model, model_contents, model_locations):
    """It should be possible to delete something replaced"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target1 = (file_name, 'expr_stmt', 0)
    target2 = (file_name, 'comment', 0)
    print(new_locations[file_name]['expr_stmt'])
    assert xml_model.do_replace(model_contents, model_locations, new_contents, new_locations, target1, target2)
    print(new_locations[file_name]['expr_stmt'])
    assert xml_model.do_delete(model_contents, model_locations, new_contents, new_locations, target1)
    dump = xml_model.dump(model_contents[file_name])
    new_dump = xml_model.dump(new_contents[file_name])
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

def test_insertion1(xml_model, model_contents, model_locations):
    """Insertion should work"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target1 = (file_name, '_inter_block', 10)
    target2 = (file_name, 'expr_stmt', 1)
    assert xml_model.do_insert(model_contents, model_locations, new_contents, new_locations, target1, target2)
    dump = xml_model.dump(model_contents[file_name])
    new_dump = xml_model.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -7,6 +7,7 @@
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
         delay();
+        a = b;
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(dump, new_dump, expected)

def test_insertion2(xml_model, model_contents, model_locations):
    """Insertion should be applied in order"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target1 = (file_name, '_inter_block', 10)
    target2 = (file_name, 'expr_stmt', 1)
    target3 = (file_name, 'expr_stmt', 0)
    assert xml_model.do_insert(model_contents, model_locations, new_contents, new_locations, target1, target2)
    assert xml_model.do_insert(model_contents, model_locations, new_contents, new_locations, target1, target3)
    dump = xml_model.dump(model_contents[file_name])
    new_dump = xml_model.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -6,6 +6,8 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
+        delay();
+        a = b;
         delay();
 
         // Sort the sides so that a <= b <= c
"""
    assert_diff(dump, new_dump, expected)

def test_insertion3(xml_model, model_contents, model_locations):
    """Insertion locations should be correctly updated"""
    file_name = 'Triangle.java.xml'
    new_contents = copy.deepcopy(model_contents)
    new_locations = copy.deepcopy(model_locations)
    target1 = (file_name, '_inter_block', 10)
    target2 = (file_name, 'expr_stmt', 1)
    target3 = (file_name, 'expr_stmt', 0)
    target4 = (file_name, '_inter_block', 9)
    target5 = (file_name, '_inter_block', 11)
    assert xml_model.do_insert(model_contents, model_locations, new_contents, new_locations, target1, target2)
    assert xml_model.do_insert(model_contents, model_locations, new_contents, new_locations, target1, target3)
    assert xml_model.do_insert(model_contents, model_locations, new_contents, new_locations, target4, target2)
    assert xml_model.do_insert(model_contents, model_locations, new_contents, new_locations, target5, target2)
    dump = xml_model.dump(model_contents[file_name])
    new_dump = xml_model.dump(new_contents[file_name])
    expected = """--- 
+++ 
@@ -6,9 +6,13 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
+        a = b;
+        delay();
+        a = b;
         delay();
 
         // Sort the sides so that a <= b <= c
+        a = b;
         if (a > b) {
             int tmp = a;
             a = b;
"""
    assert_diff(dump, new_dump, expected)

@pytest.mark.parametrize('xml,output', [
    ('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<unit xmlns="http://www.srcML.org/srcML/src" xmlns:cpp="http://www.srcML.org/srcML/cpp" revision="1.0.0" language="C" filename="rotate.c"><cpp:include>#<cpp:directive>include</cpp:directive> <cpp:file>"rotate.h"</cpp:file></cpp:include>

<comment type="line">// rotate three values</comment>
<function><type><name>void</name></type> <name>rotate</name><parameter_list>(<parameter><decl><type><name>int</name><modifier>&amp;</modifier></type> <name>n1</name></decl></parameter>, <parameter><decl><type><name>int</name><modifier>&amp;</modifier></type> <name>n2</name></decl></parameter>, <parameter><decl><type><name>int</name><modifier>&amp;</modifier></type> <name>n3</name></decl></parameter>)</parameter_list> <block>{<block_content>
  <comment type="line">// copy original values</comment>
  <decl_stmt><decl><type><name>int</name></type> <name>tn1</name> <init>= <expr><name>n1</name></expr></init></decl>, <decl><type ref="prev"/><name>tn2</name> <init>= <expr><name>n2</name></expr></init></decl>, <decl><type ref="prev"/><name>tn3</name> <init>= <expr><name>n3</name></expr></init></decl>;</decl_stmt>
  <comment type="line">// move</comment>
  <expr_stmt><expr><name>n1</name> <operator>=</operator> <name>tn3</name></expr>;</expr_stmt>
  <expr_stmt><expr><name>n2</name> <operator>=</operator> <name>tn1</name></expr>;</expr_stmt>
  <expr_stmt><expr><name>n3</name> <operator>=</operator> <name>tn2</name></expr>;</expr_stmt>
</block_content>}</block></function>
</unit>''','''#include "rotate.h"

// rotate three values
void rotate(int& n1, int& n2, int& n3) {
  // copy original values
  int tn1 = n1, tn2 = n2, tn3 = n3;
  // move
  n1 = tn3;
  n2 = tn1;
  n3 = tn2;
}
''')
])
def test_build_and_strip(xml, output):
    assert XmlModel.strip_xml_from_tree(XmlModel.string_to_tree(xml)).strip() == output.strip()
