import difflib

def assert_diff(str1, str2, expected):
    diff = list(difflib.unified_diff([s+"\n" for s in str1.split("\n")],
                                     [s+"\n" for s in str2.split("\n")]))
    expected_list = expected.split("\n")
    for line in diff:
        print(line, end="")
    assert ''.join(diff) == expected
