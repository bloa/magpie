# Algorithm Configuration

Magpie can optimise the setting of the target algorithm parameters.

To that purpose, one should provide a `.params` file and use the `ParamSetting` edit type.
Algorithm configuration can either take place independently, if `ParamSetting` is the only possible edits, or concurrently when other types of edits are also used.

The string compiled using the parameters names and values is used for both test and run commands.
Depending on the target algorithm expects to be set one should expect to write a wrapper script to handle how parameters are specified on the command line, also Magpie should be able to handle most simple cases.


# Parameter File

We provide two examples of parameter files for use in the MiniSAT [tutorial](tutorial.md).

Here is part of the `examples/code/minisat_setup/minisat_simplified.params` file:

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


Magpie parses five types of lines.

1. Empty lines and comments, that are ignored;
2. Magic constants, that change how parameters are invoked during execution;
3. Parameter definitions, that require a name, a range of possible values, and a default value;
4. Conditional parameters; and
5. Forbidden parameter combinations.

## Comments

Empty lines and lines starting with the character "`#`" are ignored (e.g., the line "`# core`" in the above example).
Comments can also be added after any other valid line of the parameter file.

## Magic constants

There are nine magic constants that can be set.

- `TIMING="test run"`
- `CLI_PREFIX="--"`
- `CLI_GLUE="="`
- `CLI_BOOLEAN="show"`
- `CLI_BOOLEAN_PREFIX_TRUE=""`
- `CLI_BOOLEAN_PREFIX_FALSE="no-"`
- `CLI_NONE="show"`
- `SILENT_PREFIX="@"`
- `SILENT_SUFFIX="$"`

The `TIMING` string specifies for which of the "setup", "compile", "test", and or "run" steps the command line is modified to use the parameter values of the current configuration file.

The `CLI_PREFIX` string is used at the start of every parameter name, whilst `CLI_GLUE` is used between the name and the value of the parameter.
For example, MiniSAT expects parameters such as "`-gc-frac=0.2`".

`CLI_BOOLEAN` accepts three values: `show`, `hide`, and `prefix`.  
The value `show` means that Booleans are passed as any other values (e.g., "`-luby=True`").
The value `hide` means that the parameter is only used when the value is true (i.e., "`-luby`" when true, and nothing when false).
Finally, the value `prefix` change the names of Boolean parameters according to their values (e.g., to obtain "`-luby`" when true and "`-no-luby`" when false).

`CLI_NONE` accepts two values: `show`, and `hide`.  
Similarly to `CLI_BOOLEAN` it enable hiding parameters when the associated value is `None`.
The value `show` means that the parameter is actually used (e.g., "--foo=None").
Conversely, the value `hide` means that the parameter absent from the final command line.

The `SILENT_PREFIX` string is used to hide parameters with matching prefix in the final command line.
Similarly, the `SILENT_SUFFIX` is used to specify a suffix which will be hidden in the final command line.

## Parameter definitions

Definitions require a name, a range of possible values, and a default value.

There are three types of ranges of values: categorical, continuous, and integer.

Magpie accept the following formats:

    NAME {VALUE, ...} [DEFAULT] # categorical
    NAME (MIN, MAX) [DEFAULT] # continuous
    NAME e(MIN, MAX) [DEFAULT] # continuous (exponential distribution)
    NAME [MIN, MAX] [DEFAULT] # integer
    NAME g[MIN, MAX] [DEFAULT] # integer (geometric distribution)


Categorical values are specified using curly braces and values separated with commas (e.g., see the "`luby`" parameter).
Spaces at the beginning and end of possible values are ignored.

A range of continuous values is specified using parentheses (e.g., see the "`var-decay`" parameter).
Values are drawn uniformly at random, unless the prefix `e` is used (e.g., see the "`gc-frac`" parameter) in which case they will be drawn following an exponential law.

A range of integer values is specified using braces (e.g., see the "`phase-saving`" parameter).
Values are drawn uniformly at random, unless the prefix `g` is used (e.g., see the "`rfirst`" parameter) in which case they will be drawn following an geometric law.

## Conditional parameters

Some parameters should only appear conditionally to the value of another parameter.

Magpie accept the following format:

    NAME | NAME == VALUE

E.g., in `examples/code/minisat_setup/minisat_advanced.params`:

    sub-lim$unbounded | @sub-lim$flag == True
    sub-lim$bounded   | @sub-lim$flag == False

Depending on the value of the hidden `@sub-lim$flag` parameter the command line will contain either the value of `sub-lim$unbounded` or `sub-lim$bounded`.
Because silent suffixes are discarded, in both cases that value will be associated to the parameter name `sub-lim`.

## Forbidden combinations

Similarly, some combinations of parameters should never occur simultaneously.
Magpie accept the following format:

    {NAME == VALUE , ...}

Any number of parameters can be specified (but at least two) as long as they are comma-separated.
