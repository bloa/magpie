# ParamsFileConfigModel

Magpie supports automated configuration of command line parameters through the `ParamsFileConfigModel` model.
This model supports configuration files that describe abstract search spaces that will then be evolved just like code or data.
By default, this model is automatically used to handle .params file.
The associated edit type is `ParamSetting`.

Depending on whether `ParamSetting` is the only edit type specified, algorithm configuration can either take place independently or combined for joint optimisation.


# Parameter File

Magpie .params format supports five types of lines:
1. Empty lines and comments, ignored during parsing;
2. Magic constants, specifying CLI formatting;
3. Parameter definitions, including a name, a range of possible values, and a default value;
4. Conditional parameters; and
5. Forbidden combinations.

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

In some cases, a parameter should only appear on the command line if another parameter is set to a specific value.
This is especially useful when certain options are only relevant under specific modes or configurations.

Magpie allows you to express such dependencies directly within the parameter file using the following format

    PARAM | CONDITION

where:
- `PARAM` is the name of the parameter that will be included _only_ if the condition holds, and
- `CONDITION` is a logical condition of the form `OTHER_PARAM == VALUE`.

### Example

Suppose we want a parameter `foo` that can take wither:
- a positive continuous value, or
- one of three special-meaning negative integers `-1`, `-2`, or `-3`.

We can express this in Magpie as follows:

```
foo$continuous e(0, 999999)[1]
foo$integer    [-3, -1][-1]
@foo$flag      {True, False}[True]

foo$continuous | @foo$flag == True
foo$integer    | @foo$flag == False
```

This setup defines three parameters:
- `foo$continuous`, which covers the continuous range of positive values;
- `foo$integer`, which includes the three special negative values; and
- `@foo$flag`, a hidden categorical parameter that controls which of the two is active.

Both `foo$continuous` and `foo$integer` use the silent suffix `$`, so regardless of which is selected, it will appear on the final command-line as `--foo=value`.
Similarly, the controller parameter `@foo$flag` uses the silent prefix `@`, meaning it will be excluded of the final command line as well.

The two conditional lines ensure that:
- if `@foo$flag` is `True`, then only `foo$continuous` is included; and that
- if `@foo$flag` is `False`, then only `foo$integer` is included.

Thanks to the silent prefix and suffix mechanisms, and the conditional rules, the resulting command line will look clean and consistent---e.g., `--foo=5.0` or `--foo=-1`---without exposing the internal selection logic.


## Forbidden combinations

There may be situations where certain combinations of parameter values should be avoided altogether---for example, if they lead to invalid behaviour, crashes, or logically inconsistent settings.

Magpie lets you specify such constraints using the following format:

    {PARAM1 == VALUE1, PARAM2 == VALUE2, ...}

This indicates that the listed combination of parameter values is not allowed and should never be sampled or evaluated.
