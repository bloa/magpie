import argparse
import pathlib
import sys

from magpie.models.xml import XmlModel

# ================================================================================
# Main function
# ================================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Magpie XML formatting remover')
    parser.add_argument('file', default='stdin', nargs='?')
    args = parser.parse_args()

    if args.file == 'stdin':
        full = sys.stdin.read()
    else:
        with pathlib.Path(args.file).open('r') as f:
            full = f.read()
    output = XmlModel.strip_xml_from_tree(XmlModel.string_to_tree(full))
    print(output)
