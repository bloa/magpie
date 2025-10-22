import collections


Token = collections.namedtuple('Token', ['type', 'value'])

KEYWORDS = {'and', 'or', 'xor', 'not', 'if', 'iif', 'in'}
MULTI_CHAR_OPS = {'==', '!=', '<=', '>=', '**'}
SINGLE_CHAR_OPS = {'+', '-', '*', '/', '<', '>', '!', '='}
IDENTIFIERS_CHARS = {'_', '$', '@'}
IDENTIFIERS_CHARS_NOLEAD = {'-'}

def tokenize(s):
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]

        if c.isspace():
            i += 1
            continue

        # numbers
        if c.isdigit():
            start = i
            has_dot = False
            while i < len(s) and (s[i].isdigit() or (s[i] == '.' and not has_dot)):
                if s[i] == '.':
                    has_dot = True
                i += 1
            num = s[start:i]
            value = float(num) if has_dot else int(num)
            tokens.append(Token('NUMBER', value))

        # string literals
        elif c in ('"', "'"):
            quote = c
            i += 1
            start = i
            while i < len(s) and s[i] != quote:
                if s[i] == '\\':
                    i += 2  # skip escaped char
                else:
                    i += 1
            if i >= len(s):
                msg = 'Unterminated string literal'
                raise SyntaxError(msg)
            raw = s[start:i]
            tokens.append(Token('STRING', raw))
            i += 1  # skip closing quote

        # identifiers and keywords
        elif c.isidentifier() or c in IDENTIFIERS_CHARS:
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] in IDENTIFIERS_CHARS or s[i] in IDENTIFIERS_CHARS_NOLEAD):
                i += 1
            word = s[start:i]
            if word in KEYWORDS:
                tokens.append(Token('OP', word))
            elif word == 'True':
                tokens.append(Token('BOOL', True))
            elif word == 'False':
                tokens.append(Token('BOOL', False))
            elif word == 'inf':
                tokens.append(Token('NUMBER', float(word)))
            else:
                tokens.append(Token('VAR', word))

        # lists and parentheses
        elif c in {'[', ']', '(', ')', ','}:
            tmp = {'[': 'LBRACK', ']': 'RBRACK', '(': 'LPAREN', ')': 'RPAREN', ',': 'COMMA'}
            tokens.append(Token(tmp[c], c))
            i += 1

        # operators
        elif c in SINGLE_CHAR_OPS:
            next_two = s[i:i+2]
            if next_two in MULTI_CHAR_OPS:
                tokens.append(Token('OP', next_two))
                i += 2
            elif c == '!':
                tokens.append(Token('OP', 'not'))
                i += 1
            else:
                tokens.append(Token('OP', c))
                i += 1

        else:
            msg = f'Unexpected character: {c}'
            raise SyntaxError(msg)

    # post-process
    merged = []
    i = 0
    while i < len(tokens):
        if tokens[i].type == 'OP' and tokens[i].value == 'not' and i + 1 < len(tokens) and tokens[i+1].type == 'OP' and tokens[i+1].value == 'in':
            merged.append(Token('OP', 'not in'))
            i += 2
        else:
            merged.append(tokens[i])
            i += 1

    return merged
