import pytest

from magpie.core import BasicSoftware, ScenarioError


@pytest.mark.parametrize(('value', 'ref'), [
    ("""
*.params : ParamFileConfigModel
*.xml : SrcmlModel
* : LineModel""", [
    ('*.params', 'ParamFileConfigModel'),
    ('*.xml', 'SrcmlModel'),
    ('*', 'LineModel'),
]),
    ("""*.params : ParamFileConfigModel

*.xml : SrcmlModel

    * : LineModel""", [
    ('*.params', 'ParamFileConfigModel'),
    ('*.xml', 'SrcmlModel'),
    ('*', 'LineModel'),
]),
    ('   foo   :   LineModel   ', [('foo', 'LineModel')]),
    ('', []),
])
def test_init_model_rules(value, ref):
    assert BasicSoftware._init_model_rules(value) == ref

@pytest.mark.parametrize('value', [
    'foo',
    """

    """,
    '* : : LineModel',
    '* : Line-Model',
    '* : Line Model',
])
def test_init_model_rules_fail(value):
    with pytest.raises(ScenarioError):
        BasicSoftware._init_model_rules(value)

@pytest.mark.parametrize(('value', 'ref'), [
    ("""
*.params : [paramconfig]
*.xml : [srcml]""", [
    ('*.params', 'paramconfig'),
    ('*.xml', 'srcml'),
]),
    ("""*.params : [paramconfig]

    *.xml : [srcml]""", [
    ('*.params', 'paramconfig'),
    ('*.xml', 'srcml'),
]),
    ('   *.params    :    [paramconfig]   ', [('*.params', 'paramconfig')]),
    ('', []),
])
def test_init_model_config(value, ref):
    assert BasicSoftware._init_model_config(value) == ref

@pytest.mark.parametrize('value', [
    'foo',
    """

    """,
    '* : : [paramconfig]',
    '* : a [paramconfig]',
    '* : [paramconfig] z',
    '* : [paramconfig] [paramconfig]',
    '* : LineModel',
])
def test_init_model_config_fail(value):
    with pytest.raises(ScenarioError):
        BasicSoftware._init_model_config(value)

@pytest.mark.parametrize(('value', 'ref'), [
    ('time', ['time']),
    ('-time', ['-time']),
    ('repair time', ['repair', 'time']),
    ('repair    time', ['repair', 'time']),
    ("""
    repair
    time""", ['repair', 'time']),
    ('perf<foo>', ['perf<foo>']),
    ('perf<foo> time', ['perf<foo>', 'time']),
    ('perf<foo bar>  -perf<bar baz>', ['perf<foo bar>', '-perf<bar baz>']),
])
def test_init_model_fitness(value, ref):
    assert BasicSoftware._init_model_fitness(value) == ref

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
    assert BasicSoftware._str_to_int_or_none(s) == ref

@pytest.mark.parametrize('s', ['foo', 'foo 1', '1 foo'])
def test_str_to_int_or_none_fail(s):
    with pytest.raises(ValueError):
        BasicSoftware._str_to_int_or_none(s)

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
    assert BasicSoftware._str_to_float_or_none(s) == ref

@pytest.mark.parametrize('s', ['foo', 'foo 1', '1 foo'])
def test_str_to_float_or_none_fail(s):
    with pytest.raises(ValueError):
        BasicSoftware._str_to_float_or_none(s)

@pytest.mark.parametrize(('s', 'ref'), [
    ('', None),
    ('   ', None),
    ('None', None),
    ('none', None),
    ('foo', 'foo'),
    ('  bar  ', 'bar'),
])
def test_str_to_str_or_none(s, ref):
    assert BasicSoftware._str_to_str_or_none(s) == ref
