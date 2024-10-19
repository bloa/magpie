from magpie.core import AbstractEdit, Patch


def test_str_no_data():
    p = Patch()
    assert str(p) == ''

def test_str_single_edit():
    e = AbstractEdit('target_file')
    p = Patch([e])
    assert str(p) == str(e)

def test_str_multiple_edits():
    e1 = AbstractEdit('target_file')
    e2 = AbstractEdit('target_file', 'data1')
    e3 = AbstractEdit('target_file', 'data2')
    p = Patch([e1, e2, e3])
    assert str(p) == f'{e1} | {e2} | {e3}'

def test_equality_no_data():
    """Equality by value"""
    p1 = Patch()
    p2 = Patch()
    assert p1 == p2

def test_equality_same_data():
    """Equality by value"""
    e1 = AbstractEdit('target_file', 'data')
    e2 = AbstractEdit('target_file', 'data')
    p1 = Patch([e1])
    p2 = Patch([e2])
    assert p1 == p2

def test_equality_different_data():
    """Equality by value"""
    e = AbstractEdit('target_file', 'data')
    p1 = Patch()
    p2 = Patch([e])
    assert p1 != p2

