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

@pytest.mark.parametrize(('expr', 'ref'), [
    ('time', [['time']]),
    ('-time', [['time']]),
    ('repair ; time', [['repair'], ['time']]),
    ('(repair + time)/2', [['repair', 'time']]),
    ('repair  ;  time', [['repair'], ['time']]),
    ("""
    repair
    time""", [['repair'], ['time']]),
    ('perf<foo>', [['perf<foo>']]),
    ('perf<foo> ; time', [['perf<foo>'], ['time']]),
    ('perf<foo bar> ; -perf<bar baz>', [['perf<foo bar>'], ['perf<bar baz>']]),
])
def test_init_model_fitness(expr, ref):
    trees = BasicSoftware._init_model_fitness(expr)
    assert [tree.variables for tree in trees] == ref
