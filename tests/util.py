import difflib


def assert_diff(str1, str2, expected):
    diff = list(difflib.unified_diff([s+'\n' for s in str1.split('\n')],
                                     [s+'\n' for s in str2.split('\n')]))
    expected_list = expected.splitlines(keepends=True)
    for line, oracle in zip(diff, expected_list):
        print(repr(line), end='')
        print(repr(oracle), end='')
        assert line == oracle
