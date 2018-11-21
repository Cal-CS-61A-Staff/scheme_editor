import argparse

parser = argparse.ArgumentParser(description="Rahul's Scheme IDE!")
parser.add_argument("file",
                    nargs="?",
                    type=argparse.FileType('rw'),
                    default=None,
                    help="Scheme file to open")
parser.add_argument("-d", "--debug",
                    help="Enable debug mode",
                    action="store_true")
parser.add_argument("-t", "--terminal")
args = parser.parse_args()
print(args.file)
