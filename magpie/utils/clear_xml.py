import argparse
import re
import sys
from xml.etree import ElementTree

from magpie.models.xml import XmlModel

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
    output = XmlModel.strip_xml_from_tree(XmlModel.string_to_tree(full))
    print(output)
