import copy
import os
import pytest

from magpie.models.xml import XmlModel, SrcmlModel
from .util import assert_diff


@pytest.fixture
def xml_model():
    return XmlModel()

@pytest.fixture
def srcml_model():
    return SrcmlModel()

@pytest.fixture
def model_contents(xml_model):
    file_name = 'triangle.c.xml'
    path = os.path.join('examples', 'code', 'triangle-c_slow', file_name)
    return {file_name: xml_model.get_contents(path)}


def test_process_blocks(srcml_model, model_contents):
    filename = 'triangle.c.xml'
    tree = model_contents[filename]
    tree = tree[2][3]
    oracle = '''<block>{
  <decl_stmt><decl><type><name>double</name></type> <name>tmp</name></decl>;</decl_stmt>

  <expr_stmt><expr><call><name>delay</name><argument_list>()</argument_list></call></expr>;</expr_stmt>

  <comment type="line">// Sort the sides so that a &lt;= b &lt;= c</comment>
  <if>if<condition>(<expr><name>a</name> <operator>&gt;</operator> <name>b</name></expr>)</condition><then> <block>{
    <expr_stmt><expr><name>tmp</name> <operator>=</operator> <name>a</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>a</name> <operator>=</operator> <name>b</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>b</name> <operator>=</operator> <name>tmp</name></expr>;</expr_stmt>
  }</block></then></if>

  <if>if<condition>(<expr><name>a</name> <operator>&gt;</operator> <name>c</name></expr>)</condition><then> <block>{
    <expr_stmt><expr><name>tmp</name> <operator>=</operator> <name>a</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>a</name> <operator>=</operator> <name>c</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>c</name> <operator>=</operator> <name>tmp</name></expr>;</expr_stmt>
  }</block></then></if>

  <if>if<condition>(<expr><name>b</name> <operator>&gt;</operator> <name>c</name></expr>)</condition><then> <block>{
    <expr_stmt><expr><name>tmp</name> <operator>=</operator> <name>b</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>b</name> <operator>=</operator> <name>c</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>c</name> <operator>=</operator> <name>tmp</name></expr>;</expr_stmt>
  }</block></then></if>

  <if>if<condition>(<expr><name>a</name> <operator>+</operator> <name>b</name> <operator>&lt;=</operator> <name>c</name></expr>)</condition><then>
    <block type="pseudo"><return>return <expr><name>INVALID</name></expr>;</return></block></then></if>
  <if>if<condition>(<expr><name>a</name> <operator>==</operator> <name>b</name> <operator>&amp;&amp;</operator> <name>b</name> <operator>==</operator> <name>c</name></expr>)</condition><then>
    <block type="pseudo"><return>return <expr><name>EQUILATERAL</name></expr>;</return></block></then></if>
  <if>if<condition>(<expr><name>a</name> <operator>==</operator> <name>b</name> <operator>||</operator> <name>b</name> <operator>==</operator> <name>c</name></expr>)</condition><then>
    <block type="pseudo"><return>return <expr><name>ISOSCELES</name></expr>;</return></block></then></if>
  <return>return <expr><name>SCALENE</name></expr>;</return>
}</block>'''
    assert srcml_model.tree_to_string(tree).strip() == oracle
    srcml_model.process_pseudo_blocks(tree)
    oracle = '''<block>{
  <decl_stmt><decl><type><name>double</name></type> <name>tmp</name></decl>;</decl_stmt>

  <expr_stmt><expr><call><name>delay</name><argument_list>()</argument_list></call></expr>;</expr_stmt>

  <comment type="line">// Sort the sides so that a &lt;= b &lt;= c</comment>
  <if>if<condition>(<expr><name>a</name> <operator>&gt;</operator> <name>b</name></expr>)</condition><then> <block>{
    <expr_stmt><expr><name>tmp</name> <operator>=</operator> <name>a</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>a</name> <operator>=</operator> <name>b</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>b</name> <operator>=</operator> <name>tmp</name></expr>;</expr_stmt>
  }</block></then></if>

  <if>if<condition>(<expr><name>a</name> <operator>&gt;</operator> <name>c</name></expr>)</condition><then> <block>{
    <expr_stmt><expr><name>tmp</name> <operator>=</operator> <name>a</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>a</name> <operator>=</operator> <name>c</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>c</name> <operator>=</operator> <name>tmp</name></expr>;</expr_stmt>
  }</block></then></if>

  <if>if<condition>(<expr><name>b</name> <operator>&gt;</operator> <name>c</name></expr>)</condition><then> <block>{
    <expr_stmt><expr><name>tmp</name> <operator>=</operator> <name>b</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>b</name> <operator>=</operator> <name>c</name></expr>;</expr_stmt>
    <expr_stmt><expr><name>c</name> <operator>=</operator> <name>tmp</name></expr>;</expr_stmt>
  }</block></then></if>

  <if>if<condition>(<expr><name>a</name> <operator>+</operator> <name>b</name> <operator>&lt;=</operator> <name>c</name></expr>)</condition><then>
    <block>/*auto*/{
      <return>return <expr><name>INVALID</name></expr>;</return>
    }/*auto*/</block></then></if>
  <if>if<condition>(<expr><name>a</name> <operator>==</operator> <name>b</name> <operator>&amp;&amp;</operator> <name>b</name> <operator>==</operator> <name>c</name></expr>)</condition><then>
    <block>/*auto*/{
      <return>return <expr><name>EQUILATERAL</name></expr>;</return>
    }/*auto*/</block></then></if>
  <if>if<condition>(<expr><name>a</name> <operator>==</operator> <name>b</name> <operator>||</operator> <name>b</name> <operator>==</operator> <name>c</name></expr>)</condition><then>
    <block>/*auto*/{
      <return>return <expr><name>ISOSCELES</name></expr>;</return>
    }/*auto*/</block></then></if>
  <return>return <expr><name>SCALENE</name></expr>;</return>
}</block>'''
    assert srcml_model.tree_to_string(tree).strip() == oracle

def test_process_literals(srcml_model, model_contents):
    filename = 'triangle.c.xml'
    tree = model_contents[filename]
    tree = tree[1][3][0]
    oracle = '<decl_stmt><decl><type><specifier>const</specifier> <name><name>struct</name> <name>timespec</name></name></type> <name>ms</name> <init>= <expr><block>{<expr><literal type="number">0</literal></expr>, <expr><literal type="number">0.001</literal><operator>*</operator><literal type="number">1e9</literal></expr>}</block></expr></init></decl>;</decl_stmt>'
    assert srcml_model.tree_to_string(tree).strip() == oracle
    srcml_model.process_literals(tree)
    oracle = '<decl_stmt><decl><type><specifier>const</specifier> <name><name>struct</name> <name>timespec</name></name></type> <name>ms</name> <init>= <expr><block>{<expr><literal_number>0</literal_number></expr>, <expr><literal_number>0.001</literal_number><operator>*</operator><literal_number>1e9</literal_number></expr>}</block></expr></init></decl>;</decl_stmt>'
    assert srcml_model.tree_to_string(tree).strip() == oracle

def test_process_operators(srcml_model, model_contents):
    filename = 'triangle.c.xml'
    tree = model_contents[filename]
    tree = tree[1][3][0]
    oracle = '<decl_stmt><decl><type><specifier>const</specifier> <name><name>struct</name> <name>timespec</name></name></type> <name>ms</name> <init>= <expr><block>{<expr><literal type="number">0</literal></expr>, <expr><literal type="number">0.001</literal><operator>*</operator><literal type="number">1e9</literal></expr>}</block></expr></init></decl>;</decl_stmt>'
    assert srcml_model.tree_to_string(tree).strip() == oracle
    srcml_model.process_operators(tree)
    oracle = '<decl_stmt><decl><type><specifier>const</specifier> <name><name>struct</name> <name>timespec</name></name></type> <name>ms</name> <init>= <expr><block>{<expr><literal type="number">0</literal></expr>, <expr><literal type="number">0.001</literal><operator_arith>*</operator_arith><literal type="number">1e9</literal></expr>}</block></expr></init></decl>;</decl_stmt>'
    assert srcml_model.tree_to_string(tree).strip() == oracle
