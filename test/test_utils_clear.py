import ast
import glob

import pytest

from utils.clear_xml import string_to_tree, strip_xml_from_tree

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
    assert strip_xml_from_tree(string_to_tree(xml)).strip() == output.strip()
