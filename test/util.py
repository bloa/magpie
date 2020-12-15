import difflib

def assert_diff(str1, str2, expected):
    diff = list(difflib.unified_diff([s+"\n" for s in str1.split("\n")],
                                     [s+"\n" for s in str2.split("\n")]))
    expected_list = expected.split("\n")
    for line in diff:
        print(line, end="")
    for i in range(len(diff)):
        assert diff[i] == expected_list[i] + "\n"
