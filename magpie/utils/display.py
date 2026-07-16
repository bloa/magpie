import re


def format_bold(text):
    return f'\033[1m{text}\033[0m'

def format_header(title, fancy=False):
    header = f'==== {title} ===='
    if fancy:
        return format_bold(header)
    return header

def format_subheader(title, fancy=False):
    header = f'~~~~ {title} ~~~~'
    if fancy:
        return format_bold(header)
    return header

def format_diff(diff, fancy=False):
    if not fancy:
        return diff
    out = diff[:]
    for patt, repl in [
            (r'^(\*\*\*\*.*)$', r'\033[36m\1\033[0m'),
            (r'^(--- .* ----)$', r'\033[36m\1\033[0m'),
            (r'^(\*\*\* .* \*\*\*\*)$', r'\033[36m\1\033[0m'),
            (r'^((?:---|\+\+\+|\*\*\*) .*)$', r'\033[1m\1\033[0m'),
            (r'^(-.*)$', r'\033[31m\1\033[0m'),
            (r'^(\+.*)$', r'\033[32m\1\033[0m'),
            (r'^(!.*)$', r'\033[33m\1\033[0m'),
            (r'^(@@ .* @@)', r'\033[36m\1\033[0m'),
    ]:
        out = re.sub(patt, repl, out, flags=re.MULTILINE)
    return out
