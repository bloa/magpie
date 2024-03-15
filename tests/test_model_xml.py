import contextlib
import copy
import pathlib

import pytest

from magpie.models.xml import XmlModel

from .util import assert_diff


@pytest.fixture()
def xml_model():
    model = XmlModel('Triangle.java.xml')
    with contextlib.chdir(pathlib.Path('tests') / 'examples'):
        model.init_contents()
    return model

@pytest.fixture()
def file_contents():
    path = pathlib.Path('tests') / 'examples' / 'Triangle.java'
    with path.open('r') as myfile:
        return myfile.read()

def test_dump(xml_model, file_contents):
    """Immediate dump should be transparent"""
    dump = xml_model.dump()
    assert dump == file_contents

def test_deletion1(xml_model):
    """Deletion should work"""
    variant = copy.deepcopy(xml_model)
    target = ('Triangle.java.xml', 'expr_stmt', 0)
    assert variant.do_delete(target)
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(xml_model.dump(), variant.dump(), expected)

def test_deletion2(xml_model):
    """Deletions should only be applied once"""
    variant = copy.deepcopy(xml_model)
    target = ('Triangle.java.xml', 'expr_stmt', 0)
    assert variant.do_delete(target)
    assert not variant.do_delete(target)

def test_replacement1(xml_model):
    """Identical replacements should not be applied"""
    variant = copy.deepcopy(xml_model)
    target1 = ('Triangle.java.xml', 'expr_stmt', 3)
    assert not variant.do_replace(xml_model, target1, target1)

def test_replacement2(xml_model):
    """Replacement should work"""
    variant = copy.deepcopy(xml_model)
    target1 = ('Triangle.java.xml', 'expr_stmt', 0)
    target2 = ('Triangle.java.xml', 'comment', 0)
    assert not variant.do_replace(xml_model, target1, target1)
    assert variant.do_replace(xml_model, target1, target2)
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        // Sort the sides so that a <= b <= c
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(xml_model.dump(), variant.dump(), expected)

def test_replacement3(xml_model):
    """Identical replacements should not be applied (even after replacement)"""
    variant = copy.deepcopy(xml_model)
    target1 = ('Triangle.java.xml', 'expr_stmt', 0)
    target2 = ('Triangle.java.xml', 'comment', 0)
    assert not variant.do_replace(xml_model, target1, target1)
    assert variant.do_replace(xml_model, target1, target2)
    assert not variant.do_replace(xml_model, target1, target2)
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        // Sort the sides so that a <= b <= c
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(xml_model.dump(), variant.dump(), expected)

def test_deletethenreplace(xml_model):
    """It should be possible to replace something deleted"""
    variant = copy.deepcopy(xml_model)
    target1 = ('Triangle.java.xml', 'expr_stmt', 0)
    target2 = ('Triangle.java.xml', 'comment', 0)
    assert variant.do_delete(target1)
    assert variant.do_replace(xml_model, target1, target2)
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        // Sort the sides so that a <= b <= c
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(xml_model.dump(), variant.dump(), expected)

def test_replacethendelete(xml_model):
    """It should be possible to delete something replaced"""
    variant = copy.deepcopy(xml_model)
    target1 = ('Triangle.java.xml', 'expr_stmt', 0)
    target2 = ('Triangle.java.xml', 'comment', 0)
    assert variant.do_replace(xml_model, target1, target2)
    assert variant.do_delete(target1)
    expected = """--- 
+++ 
@@ -6,7 +6,7 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
-        delay();
+        
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(xml_model.dump(), variant.dump(), expected)

def test_insertion1(xml_model):
    """Insertion should work"""
    variant = copy.deepcopy(xml_model)
    target1 = ('Triangle.java.xml', '_inter_block', 10)
    target2 = ('Triangle.java.xml', 'expr_stmt', 1)
    assert variant.do_insert(xml_model, target1, target2)
    expected = """--- 
+++ 
@@ -7,6 +7,7 @@
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
         delay();
+        a = b;
 
         // Sort the sides so that a <= b <= c
         if (a > b) {
"""
    assert_diff(xml_model.dump(), variant.dump(), expected)

def test_insertion2(xml_model):
    """Insertion should be applied in order"""
    variant = copy.deepcopy(xml_model)
    target1 = ('Triangle.java.xml', '_inter_block', 10)
    target2 = ('Triangle.java.xml', 'expr_stmt', 1)
    target3 = ('Triangle.java.xml', 'expr_stmt', 0)
    assert variant.do_insert(xml_model, target1, target2)
    assert variant.do_insert(xml_model, target1, target3)
    expected = """--- 
+++ 
@@ -6,6 +6,8 @@
 
     public static TriangleType classifyTriangle(int a, int b, int c) {
 
+        delay();
+        a = b;
         delay();
 
         // Sort the sides so that a <= b <= c
"""
    assert_diff(xml_model.dump(), variant.dump(), expected)

def test_insertion3(xml_model):
    """Insertion locations should be correctly updated"""
    variant = copy.deepcopy(xml_model)
    target1 = ('Triangle.java.xml', '_inter_block', 10)
    target2 = ('Triangle.java.xml', 'expr_stmt', 1)
    target3 = ('Triangle.java.xml', 'expr_stmt', 0)
    target4 = ('Triangle.java.xml', '_inter_block', 9)
    target5 = ('Triangle.java.xml', '_inter_block', 11)
    assert variant.do_insert(xml_model, target1, target2)
    assert variant.do_insert(xml_model, target1, target3)
    assert variant.do_insert(xml_model, target4, target2)
    assert variant.do_insert(xml_model, target5, target2)
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
    assert_diff(xml_model.dump(), variant.dump(), expected)

@pytest.mark.parametrize(('xml', 'output'), [
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
</unit>''', '''#include "rotate.h"

// rotate three values
void rotate(int& n1, int& n2, int& n3) {
  // copy original values
  int tn1 = n1, tn2 = n2, tn3 = n3;
  // move
  n1 = tn3;
  n2 = tn1;
  n3 = tn2;
}
'''),
])
def test_build_and_strip(xml, output):
    assert XmlModel.strip_xml_from_tree(XmlModel.string_to_tree(xml)).strip() == output.strip()
