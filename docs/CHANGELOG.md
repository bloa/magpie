# Changelog

## [1.3.0] bloa_unstable

**Changed**

- refactored protocols and scenario management
- refactored formatting options for better parsing and granularity


## [1.2.2] bloa_stable

**Fixed**

- fix colour stripping in log files

**Changed**

- refactored output formatting functions to utils folder
- refactored evaluation cache to separate class


## [1.2.1] 2026-04-28

**Added**

- add templated version of `OutputFitness`
- add support for generalised expression trees for fitness
- add support for generalised expression trees to the algorithm configuration model (conditionals, forbidden combinations, general assertions)
- add support for automatically computed parameter values
- add live command display during execution
- add support for Gradle test suites
- add support for read-only ingredient files (`ingredient_files`)
- add more ENV data (counter, patch under evaluation)

**Changed**

- added human-readable date (YYYYMMDD) to generated filenames for easier file management
- removed support for maximisation fitness (just minimise to -inf)
- changed multi-objective syntax to use ";" instead of space to enable generalised expression trees
- changed AbstractEdit to a true abstract class

**Fixed**

- fix spurious timestamp lock files during tests
- fix requirement on older CMake
- fix median computation for warmup values aggregation
- fix warmup values aggregation for multi-objective optimisation


## [1.2.0] 2025-04-22

**Added**

- add basic support for multi-objective optimisation (defaults to lexicographic)
- add support for maximisation fitness functions (defaults to minimisation)
- add support for templated fitness functions (e.g., `perf<instructions>` or `perf<branch-misses>`)
- add support for templated edits (e.g., `XmlNodeReplacement<stmt>`)
- add tentative support for Windows and non-POSIX environments
- add new and improved fitness functions (GNU time, perf)

**Changed**

- restructure fitness functions support by moving them from `magpie/core/basic_software.py` to dedicated classes in `magpie/fitness`
- restructure tests by separating core unit tests from newly added integration and script-based tests
- rename edit types to ensure class names end with "Edit" (consistent with fitness functions ending with "Fitness")
- update SrcML-based statements to use templates (e.g., in config files`SrcmlStmtReplacement` becomes `XmlNodeReplacement<stmt>`)
- improve exponential random value generation in parameter configuration
- update `magpie/scripts/python_to_xml.py` to the latest Python version

**Fixed**

- fix JUnit support for the "repair" fitness function
- fix infinite loops in GP for small search spaces (#8)
- fix instance batch output processing


## [1.1.0] 2024-04-12

TODO


## [1.0.0] 2023-10-23

Initial "official" release of Magpie

