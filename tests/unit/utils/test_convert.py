import pytest

import magpie

@pytest.mark.parametrize(('s', 'ref'), [
    ('', None),
    ('   ', None),
    ('None', None),
    ('none', None),
    ('1', 1.0),
    ('000', 0.0),
    ('9_000', 9000),
    ('5e3', 5000),
    ('-1', -1),
    ('-1.5', -1),
])
def test_str_to_int_or_none(s, ref):
    assert magpie.utils.str_to_int_or_none(s) == ref

@pytest.mark.parametrize('s', ['foo', 'foo 1', '1 foo'])
def test_str_to_int_or_none_fail(s):
    with pytest.raises(ValueError):
        magpie.utils.str_to_int_or_none(s)

@pytest.mark.parametrize(('s', 'ref'), [
    ('', None),
    ('   ', None),
    ('None', None),
    ('none', None),
    ('1', 1.0),
    ('000', 0.0),
    ('9_000', 9000.0),
    ('5e3', 5000.0),
    ('-1', -1.0),
    ('-1.5', -1.5),
])
def test_str_to_float_or_none(s, ref):
    assert magpie.utils.str_to_float_or_none(s) == ref

@pytest.mark.parametrize('s', ['foo', 'foo 1', '1 foo'])
def test_str_to_float_or_none_fail(s):
    with pytest.raises(ValueError):
        magpie.utils.str_to_float_or_none(s)

@pytest.mark.parametrize(('s', 'ref'), [
    ('', None),
    ('   ', None),
    ('None', None),
    ('none', None),
    ('foo', 'foo'),
    ('  bar  ', 'bar'),
])
def test_str_to_str_or_none(s, ref):
    assert magpie.utils.str_to_str_or_none(s) == ref

@pytest.mark.parametrize(('s', 'ref'), [
    ('True', True),
    ('TRUE', True),
    ('t', True),
    ('1', True),
    ('  false  ', False),
    ('0', False),
])
def test_str_to_bool(s, ref):
    assert magpie.utils.str_to_bool(s) == ref

@pytest.mark.parametrize('s', ['foo', 'truee', '2', '00'])
def test_str_to_bool_fail(s):
    with pytest.raises(ValueError):
        assert magpie.utils.str_to_bool(s)
