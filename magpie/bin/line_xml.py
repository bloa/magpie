import argparse
import pathlib

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MAGPIE Line XML Formatter')
    parser.add_argument('--file', type=pathlib.Path)
    parser.add_argument('--mode', type=str, default='default', choices=['default', 'line'])
    args = parser.parse_args()

    with open(args.file) as f:
        print("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
        print("<unit xmlns=\"magpie\" filename=\"{}\">".format(args.file))
        if args.mode == 'default':
            for line in f.readlines():
                print("<line>{}<\line>".format(line), end='')
        elif args.mode == 'line':
            for line in f.readlines():
                print("<line>{}<\line>".format(line.rstrip('\n')))
        print("</unit>")
