from magpie.core import AbstractEdit, TemplatedEdit

class DummyEdit(AbstractEdit):
    def apply(self, ref, variant):
        pass
    @classmethod
    def auto_create(cls, ref):
        pass

class DummyTemplatedEdit(TemplatedEdit):
    def apply(self, ref, variant):
        pass
    @classmethod
    def auto_create(cls, ref):
        pass

def test_str_no_data():
    e = DummyEdit('target_file')
    assert str(e) == "Dummy('target_file')"

def test_str_abstract_data():
    e = DummyEdit('target_file', 'data1', 'data2')
    assert str(e) == "Dummy('target_file', 'data1', 'data2')"

def test_str_complex_data():
    e = DummyEdit('target_file', ['data1', 'data2'])
    assert str(e) == "Dummy('target_file', ['data1', 'data2'])"

def test_str_complex_string_data():
    e = DummyEdit('target_file', "['data1', 'data2']")
    assert str(e) == "Dummy('target_file', \"['data1', 'data2']\")"

def test_str_template():
    e = DummyTemplatedEdit.template('<foo>')('target_file')
    assert str(e) == "Dummy<foo>('target_file')"

def test_str_template_multi():
    e = DummyTemplatedEdit.template('<foo, bar>')('target_file')
    assert str(e) == "Dummy<foo, bar>('target_file')"

def test_str_template_quote():
    e = DummyTemplatedEdit.template('<"foo, bar">')('target_file')
    assert str(e) == "Dummy<\"foo, bar\">('target_file')"
    assert len(e.TEMPLATE) == 1

def test_str_template_quotemulti():
    e = DummyTemplatedEdit.template('<"foo,bar", baz>')('target_file')
    assert str(e) == "Dummy<\"foo,bar\", baz>('target_file')"
    assert len(e.TEMPLATE) == 2

def test_equality_same_data():
    """Equality by value"""
    e1 = DummyEdit('target_file', 'data1', 'data2')
    e2 = DummyEdit('target_file', 'data1', 'data2')
    assert e1 == e2

def test_equality_different_data():
    e1 = DummyEdit('target_file', 'data1', 'data2')
    e2 = DummyEdit('target_file')
    assert e1 != e2

def test_equality_different_class():
    class Dummy2Edit(DummyEdit):
        pass
    e1 = DummyEdit('target_file')
    e2 = Dummy2Edit('target_file')
    assert e1 != e2
