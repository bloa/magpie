from magpie.core import Edit

def test_str_no_data():
    e = Edit('target_file')
    assert str(e) == "Edit('target_file')"

def test_str_basic_data():
    e = Edit('target_file', 'data1', 'data2')
    assert str(e) == "Edit('target_file', 'data1', 'data2')"

def test_str_complex_data():
    e = Edit('target_file', ['data1', 'data2'])
    assert str(e) == "Edit('target_file', ['data1', 'data2'])"

def test_str_complix_string_data():
    e = Edit('target_file', "['data1', 'data2']")
    assert str(e) == "Edit('target_file', \"['data1', 'data2']\")"

def test_str_inheritance():
    class TestEdit(Edit):
        pass
    e = TestEdit('target_file')
    assert str(e) == "TestEdit('target_file')"

def test_equality_same_data():
    """Equality by value"""
    e1 = Edit('target_file', 'data1', 'data2')
    e2 = Edit('target_file', 'data1', 'data2')
    assert e1 == e2

def test_equality_different_data():
    e1 = Edit('target_file', 'data1', 'data2')
    e2 = Edit('target_file')
    assert e1 != e2

def test_equality_different_class():
    class TestEdit(Edit):
        pass
    e1 = Edit('target_file')
    e2 = TestEdit('target_file')
    assert e1 != e2
