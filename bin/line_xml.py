import argparse
import pathlib
import re

def sanitize_xml(s):
    out = s
    out = re.sub('&', '&amp;', out)
    out = re.sub('<', '&lt;', out)
    out = re.sub('>', '&gt;', out)
    return out


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie line to XML formatter')
    parser.add_argument('--file', type=pathlib.Path)
    parser.add_argument('--indent', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--empty-lines', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--comments', type=str, default='')
    parser.add_argument('--multi-line-comments', type=str, default='')
    parser.add_argument('--ignore', type=str, default='')
    args = parser.parse_args()

    if args.comments:
        regexp_line = r'^(\s*)(.*?)(\s*(?:(?:{}).*)?)$'.format('|'.join(args.comments.split(' ')))
    else:
        regexp_line = r'^(\s*)(.*?)(\s*)$'
    if args.multi_line_comments:
        ml_comments = args.multi_line_comments.split(' ')
    else:
        ml_comments = []
    in_ml_comment = False
    ignore_list = args.ignore.split(' ')

    with open(args.file) as f:
        print("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
        print("<unit xmlns=\"magpie\" filename=\"{}\">".format(args.file))
        for line in f.readlines():
            m = re.match(regexp_line, line.rstrip('\n'))
            a, b, c = m.groups()
            if ml_comments and not in_ml_comment and b.startswith(ml_comments[0]):
                in_ml_comment = True
            b = sanitize_xml(b)
            c = sanitize_xml(c)
            if (ml_comments and in_ml_comment) or (b in ignore_list) or not (b or args.empty_lines):
                print(a, b, c, sep='')
            else:
                print("{}<line>{}</line>{}".format(a, b, c))
            if ml_comments and in_ml_comment and b.endswith(ml_comments[1]):
                in_ml_comment = False
        print("</unit>")
