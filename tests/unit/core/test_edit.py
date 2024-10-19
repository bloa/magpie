from magpie.core import AbstractEdit, TemplatedEdit


def test_str_no_data():
    e = AbstractEdit('target_file')
    assert str(e) == "Abstract('target_file')"

def test_str_abstract_data():
    e = AbstractEdit('target_file', 'data1', 'data2')
    assert str(e) == "Abstract('target_file', 'data1', 'data2')"

def test_str_complex_data():
    e = AbstractEdit('target_file', ['data1', 'data2'])
    assert str(e) == "Abstract('target_file', ['data1', 'data2'])"

def test_str_complex_string_data():
    e = AbstractEdit('target_file', "['data1', 'data2']")
    assert str(e) == "Abstract('target_file', \"['data1', 'data2']\")"

def test_str_inheritance():
    class TestEdit(AbstractEdit):
        pass
    e = TestEdit('target_file')
    assert str(e) == "Test('target_file')"

def test_str_template():
    class TestTemplatedEdit(TemplatedEdit):
        pass
    e = TestTemplatedEdit.template('<foo>')('target_file')
    assert str(e) == "Test<foo>('target_file')"

def test_str_template_multi():
    class TestTemplatedEdit(TemplatedEdit):
        pass
    e = TestTemplatedEdit.template('<foo, bar>')('target_file')
    assert str(e) == "Test<foo, bar>('target_file')"

def test_str_template_quote():
    class TestTemplatedEdit(TemplatedEdit):
        pass
    e = TestTemplatedEdit.template('<"foo, bar">')('target_file')
    assert str(e) == "Test<\"foo, bar\">('target_file')"
    assert len(e.TEMPLATE) == 1

def test_str_template_quotemulti():
    class TestTemplatedEdit(TemplatedEdit):
        pass
    e = TestTemplatedEdit.template('<"foo,bar", baz>')('target_file')
    assert str(e) == "Test<\"foo,bar\", baz>('target_file')"
    assert len(e.TEMPLATE) == 2

def test_equality_same_data():
    """Equality by value"""
    e1 = AbstractEdit('target_file', 'data1', 'data2')
    e2 = AbstractEdit('target_file', 'data1', 'data2')
    assert e1 == e2

def test_equality_different_data():
    e1 = AbstractEdit('target_file', 'data1', 'data2')
    e2 = AbstractEdit('target_file')
    assert e1 != e2

def test_equality_different_class():
    class TestEdit(AbstractEdit):
        pass
    e1 = AbstractEdit('target_file')
    e2 = TestEdit('target_file')
    assert e1 != e2
