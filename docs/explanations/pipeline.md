# Software Evaluation Pipeline

```mermaid
flowchart LR
    A[Init] --> B[Setup]
    B --> C[Compile]
    C --> D[Test]
    D --> E[Run]
```

Magpie evaluates software variants through a structured five-step pipeline:
1. init,
2. setup,
3. compile,
4. test, and
5. run.

The _init_ and _setup_ steps are performed once, on the original software, whilst the _compile_, _test_, and _run_ steps are repeated for every software variant evaluated.

With the exception of the "repair" fitness function, any failure (i.e., a nonzero return code from any command) causes software variants to be immediately discarded.
This ensures only successfully processed variants contribute to the search.


## Init

The _init_ step is executed **only once**, on the original software, at the very beginning of a Magpie run.
Its purpose is to prepare the environment by ensuring that all necessary files are in place before modelling of the target files can begin.

Typical tasks include:
- generating auxiliary files (e.g., pre-parsed ASTs); or
- copying or syncing directories into the experiment workspace.

Unlike other steps, _init_ is **always** executed, regardless of the entry point or whether any variants need to be evaluated.

In most cases, it is recommended to skip this step by specifying an empty `[software] init_cmd`.


## Setup

The _setup_ step is also executed **only once**, on the original software, occurring after _init_  and just before the first _compile_ on the first software variant.
Its purpose is to perform expensive operations that would otherwise be repeated identically for every variant, effectively creating a checkpoint to avoid wasting resources.

Typical tasks include:
- bootstrapping a build system (e.g., running `cmake` to create a build directory);
- precompiling libraries; or
- setting up incremental compilation.

Unlike _init_, the _setup_ step is only executed when software variants are actually evaluated, and is therefore not performed in entry points such as `bin/show_patch.py`.

In the case of incremental compilation, `[software] setup_cmd` can simply be set to the same value as `[software] compile_cmd`.


## Compile

The _compile_ step is executed **once for every software variant**, after _setup_ and before the _test_ and _run_ steps.
Its purpose is to compile or prepare the variant after applying edits.

Typical tasks include:
- compiling source code (`make`, `gradle build`, etc.);
- generating intermediate files needed for testing or execution.

The _compile_ and _test_ steps are functionally identical.
However, they are separated for clarity, allowing Magpie to distinguish between compilation and testing failures during evaluation.


## Test

The _test_ step is executed **once for every software variant**, after _compile_ and before _run_.
Its purpose is to perform a lightweight check to verify that the variant behaves correctly, helping to avoid unnecessary or expensive evaluation in the subsequent _run_ step.

Typical tasks include:
- running the software test suite;
- executing the variant on a small or simplified input; or
- checking for obvious runtime errors or crashes.

In the case of the _repair_ fitness function, the fitness value is computed during this step, unlike most other scenarios where it is computed from the output of the _run_ step.


## Run

The _run_ step is executed last, for every software variant that has passed all previous steps.
Its purpose is the compute the fitness value used to optimise the original software.

If multiple training instances are specified, the _run_ step is repeated multiple times on a sample of instances, similar to _batch processing_ in machine learning.
The fitness value for the software variant is then aggregated from these individual runs and instances.
