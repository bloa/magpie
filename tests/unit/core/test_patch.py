import pytest

from magpie.core import Patch

from .test_edit import DummyEdit, DummyTemplatedEdit


@pytest.mark.parametrize(('edits', 'expected'), [
    [[], ''],
    [[DummyEdit('target_file')], "Dummy('target_file')"],
    [[DummyTemplatedEdit.template('<foo>')('target_file')], "Dummy<foo>('target_file')"],
    [[DummyEdit('target_file', 'data1'),
      DummyEdit('target_file', 'data2')],
     "Dummy('target_file', 'data1') | Dummy('target_file', 'data2')"],
])
def test_str(edits, expected):
    assert str(Patch(edits)) == expected

def test_equality_no_data():
    """Equality by value"""
    p1 = Patch()
    p2 = Patch()
    assert p1 == p2
    assert hash(p1) == hash(p2)

def test_equality_same_data():
    """Equality by value"""
    e1 = DummyEdit('target_file', 'data')
    e2 = DummyEdit('target_file', 'data')
    p1 = Patch([e1])
    p2 = Patch([e2])
    assert p1 == p2
    assert hash(p1) == hash(p2)

def test_equality_different_data():
    """Equality by value"""
    e = DummyEdit('target_file', 'data')
    p1 = Patch()
    p2 = Patch([e])
    assert p1 != p2
    assert hash(p1) != hash(p2)

@pytest.mark.parametrize('other', [
    0,
    1,
    2.0,
    True,
    [],
    [1, 2, 3],
])
def test_equality_other(other):
    p = Patch()
    assert p != other

@pytest.mark.parametrize(('target', 'data'), [
    ['target_file', []],
    ['target_file', ['foo', 'bar']],
])
def test_raw(target, data):
    e = DummyEdit(target, *data)
    h = {
            'type': 'DummyEdit',
            'target': target,
            'data': data,
        }
    assert Patch().raw() == []
    assert Patch([e]).raw() == [h]
    assert Patch([e, e]).raw() == [h, h]

@pytest.mark.parametrize('patch', [
    Patch(),
    Patch([DummyEdit('target_file')]),
    Patch([DummyEdit('target_file'), DummyEdit('target_file')]),
    Patch([DummyTemplatedEdit.template('<foo>')('target_file')]),
])
def test_from_string(patch):
    assert Patch.from_string(str(patch)) == patch
