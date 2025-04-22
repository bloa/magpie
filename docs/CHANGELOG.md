# Changelog

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

