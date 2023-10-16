import argparse
import re
import sys
from xml.etree import ElementTree

def string_to_tree(xml_str):
    xml_str = re.sub(r'(?:\s+xmlns[^=]*="[^"]+")+', '', xml_str, count=1)
    xml_str = re.sub(r'<(/?\w+?):(\w+)>', r'<\1_\2>', xml_str)
    return ElementTree.fromstring(xml_str)

def strip_xml_from_tree(tree):
    return ''.join(tree.itertext())


# ================================================================================
# Main function
# ================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magpie XML formatting remover')
    parser.add_argument('file', default='stdin', nargs='?')
    args = parser.parse_args()

    if args.file == 'stdin':
        full = sys.stdin.read()
    else:
        with open(args.file) as f:
            full = f.read()
    output = strip_xml_from_tree(string_to_tree(full))
    print(output)
