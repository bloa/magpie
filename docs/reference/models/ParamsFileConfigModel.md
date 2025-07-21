# ParamsFileConfigModel

Magpie supports automated configuration of command line parameters through the `ParamsFileConfigModel` model.
This model supports configuration files that describe abstract search spaces that will then be evolved just like code or data.
By default, this model is automatically used to handle .params file.
The associated edit type is `ParamSetting`.

Depending on whether `ParamSetting` is the only edit type specified, algorithm configuration can either take place independently or combined for joint optimisation.


# Parameter File

Magpie .params format supports six types of lines:
1. empty lines and comments, both ignored during parsing;
2. magic constants, specifying CLI formatting;
3. parameter definitions, including a name, a range of possible values, and a default value;
4. conditional parameters,
5. dynamic parameters; and
6. general assertions.

Here is an example fragment:
```
CLI_PREFIX = "-"
CLI_GLUE = "="
CLI_BOOLEAN = "prefix"

# core
luby      {True, False}[True]
rnd-init  {True, False}[False]
gc-frac   e(0, 65535)[0.2]
rinc      e(1, 65535)[2]
var-decay (0, 1)[0.95]

phase-saving [0, 2][2]
ccmin-mode   [0, 2][2]
rfirst       g[1, 65535][100]
```


## Empty lines and comments

Empty lines are ignored, as well as any text following a `#` character (e.g., the line `# core` in the above example).


## Magic constants

The .params file may specify _magic constants_ to control how parameters are translated into command-line arguments.
Their default values are:

```
TIMING="test run"
CLI_PREFIX="--"
CLI_GLUE="="
CLI_BOOLEAN="show"
CLI_BOOLEAN_PREFIX_TRUE=""
CLI_BOOLEAN_PREFIX_FALSE="no-"
CLI_NONE="show"
SILENT_PREFIX="@"
SILENT_SUFFIX="$"
```

`TIMING` controls which step ("setup", "compile", "test", or "run") is associated with the current .params file.
For example, `TIMING="compile"` would apply parameters to the `compile_cmd` command only.

`CLI_PREFIX` and `CLI_GLUE` define how parameters are formatted (e.g., `--foo=42`).

`CLI_BOOLEAN` specifies how values `True` and `False` are interpreted:
- when `show`: regular formatting (e.g., `--foo=True --bar=False`)
- when `hide`: include name only when `True` (e.g., `--foo`)
- when `prefix`: switch name based on `CLI_BOOLEAN_PREFIX_TRUE` and `CLI_BOOLEAN_PREFIX_FALSE` (e.g., `--foo --no-bar`)

`CLI_BOOLEAN` specifies how the value `None` is interpreted:
- when `show`: regular formatting (e.g., `--foo=None`)
- when `hide`: skipped entirely when `None`

The `SILENT_PREFIX` string is used to hide parameters with matching prefix in the final command line.
Similarly, the `SILENT_SUFFIX` is used to specify a suffix which will be hidden in the final command line.

These settings make it easy to adapt Magpie to the expected interface of the target software, with or without wrapper scripts.


## Parameter definitions

Definitions require a name, a range of possible values, and a default value.

Three value types are supported:
- categorical, specified with curly braces `{}`;
- continuous, specified with parentheses `()`; and
- integer, specified with square brackets `[]`.

Default values are always specified within square brackets after the value range.

### Categorical parameters

Examples:
```
foo {0, 1, 10, 11}[0]
bar {True, False}[True]
baz {A, B, C, False, None, 0}[None]
```

Values are separated by commas.
Leading and trailing whitespace around values is ignored.
`True`, `False`, and `None` are "regular" categorical values but may be formatted specially depending on magic constants.
Values are sampled uniformly at random.

### Continuous parameters

Examples:
```
foo (0, 1)[0.95]
bar (-1.0, 1.0)[0]
baz e(1, 10)[2]
```

Sampling is uniform unless the prefix `e` is used, in which case sampling follows an [exponential distribution](https://en.wikipedia.org/wiki/Exponential_distribution).
An optional `lambda` value may be added to control the distribution's rate, e.g., `baz e(1, 10, 0.5)[2]`.
The default `lambda` value is `10/(max-min)`; note that `lambda` is the inverse of the desired mean.

### Integer parameters

Examples:
```
foo [0, 1][1]
bar [-1, 1][0]
baz g[1, 10][2]
```

Sampling is uniform unless the prefix `g` is used, in which case sampling follows a [geometric distribution](https://en.wikipedia.org/wiki/Geometric_distribution).
An optional `lambda` value may be added to control the distribution's rate, e.g., `baz g[1, 10, 0.5][2]`.
The default `lambda` value is `10/(max-min)`; note that `lambda` is the inverse of the desired mean.


## Conditional parameters

Magpie supports conditional inclusion of parameters using the show directive.
This allows parameters to appear only when a specific condition holds, offering a clean and expressive way to control which parameters are visible and active in a given configuration.

Use the following syntax:

    show PARAM if EXPR

where:
- `PARAM` is the name of the parameter to conditionally including in the CLI, and
- `EXPR` is a Python-style Boolean expression that defines the condition under which the parameter is included.

Examples:

**Value-specific parameters**
```
optimizer {sgd, adam}[adam]
momentum f(0.0, 1.0)[0.9]
beta1 f(0.0, 1.0)[0.9]
beta2 f(0.0, 1.0)[0.999]

show momentum if optimizer == "sgd"
show beta1    if optimizer == "adam"
show beta2    if optimizer == "adam"
```

In this setup, the three parameters `momentum`, `beta1`, and `beta2` are conditioned to the value of the `optimizer` parameter, and only included in the CLI when relevant.

**Complex conditions**
```
scheduler {None, linear, cosine}[linear]
warmup_steps i(0, 1000)[100]

show warmup_steps if scheduler in ["linear", "cosine"] and warmup_steps > 0
```

The `warmup_steps` parameter is only used when both a scheduler is used, **and** the parameter value is meaningful.

**Multi-domain parameter**
```
foo$continuous e(0, 999999)[1]
foo$integer    [-3, -1][-1]
@foo$flag      {True, False}[True]

show foo$continuous if @foo$flag
show foo$integer    if not @foo$flag
```

This defines three parameters:
- `foo$continuous`, and
- `foo$integer`, two variants of the `--foo` flag, distinguished by `$` suffixes (hidden in the final CLI); and
- `@foo$flag`, a hidden parameter ensuring that only one variant is visible at a time.

This setup ensures that users will see clean command lines like:
```
--foo=5.0   # when @foo$flag == True
--foo=-2    # when @foo$flag == False
```
without ever seeing `@foo$flag` or the internal parameter names.

Note using a silent prefix for `@foo$flag` is equivalent to writing `show foo$flag if False` as it ensures the parameter is not included in the final CLI.


## Dynamic parameters

Magpie supports dynamic parameters using the set directive. This allows you to define parameters whose values are computed at runtime, based on the values of other parameters.

Dynamic parameters are resolved after all regular parameters have been sampled, using a Python-style expression:

    set PARAM = EXPR

where:
- `PARAM` is the name of the new or overridden parameter.
- `EXPR` is a Python-like expression that may reference any previously defined parameters.

The resulting value will be included in the final configuration and in the generated command-line, just like any other parameter.

Examples:

**Automated value computation**
```
set weight_decay = base_decay / num_params
```

**Mutually exclusive Booleans**
```
enable_x {True, False}[True]
set enable_y = not enable_x
```

**Rescaling parameter values**
```
a (0, 100)[33]
b (0, 100)[33]
c (0, 100)[33]

set @sum_abc = a + b + c
set a = a / @sum_abc
set b = b / @sum_abc
set c = c / @sum_abc
```


## General assertions

Magpie allows you to specify arbitrary constraints on parameter combinations using Python-style assertions.
This enables rich and flexible expressions to define invalid or undesirable configurations.

Use the `assert` keyword followed by any Boolean expression over parameter names:

    assert EXPR

If the assertion fails (i.e., the expression evaluates to `False`), the corresponding configuration will be automatically discarding without evaluation.

Examples:

    assert optimizer != "sgd" or learning_rate > 0
    assert not (model == "linear" and depth > 1)
    assert batch_size in [32, 64, 128]


## Legacy support

Additionally, Magpie supports alternative backward-compatible syntax for conditional parameters and forbidden combinations.

### Conditional parameters

Older versions of Magpie supported conditional parameters using a simplified syntax:

    PARAM | OTHER_PARAM == VALUE

This included the named parameter only if the condition was true.
It is equivalent to:

    show PARAM if OTHER_PARAM == VALUE

This legacy format only supports basic equality conditions (`==`) and lacks the full expressiveness of arbitrary Boolean expressions.
While still supported for backward compatibility, it is now deprecated.
Users are encouraged to migrate to the more general `show ... if ...` syntax.


### Forbidden combinations

In earlier versions of Magpie, invalid configurations were expressed using a special brace syntax:

    {PARAM1 == VALUE1, PARAM2 == VALUE2, ...}

This was a shorthand for specifying that a particular conjunction of equality conditions should be avoided.
It is equivalent to:

    assert not (PARAM1 == VALUE1 and PARAM2 == VALUE2 and ...)

This syntax is **less expressive** than `assert` and only supports simple equality conditions (`==`).
It is retained for backward compatibility but is no longer recommended.
For full flexibility and clarity, prefer using `assert EXPR` instead.
