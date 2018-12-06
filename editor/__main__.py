import argparse
import local_server

parser = argparse.ArgumentParser(description="Rahul's Scheme IDE!")
parser.add_argument("file",
                    type=argparse.FileType('r+'),
                    help="Scheme file to open")
parser.add_argument("-d", "--debug",
                    help="Enable debug mode",
                    action="store_true")
parser.add_argument("-ok", "--okpy",
                    help="start OKPY",
                    action="store_true")
parser.add_argument("-t", "--terminal")
args = parser.parse_args()

if args.okpy:
    import ok_interface
else:
    local_server.start(args.file)
