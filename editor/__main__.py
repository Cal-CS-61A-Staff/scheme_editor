import argparse
import editor.local_server as local_server

parser = argparse.ArgumentParser(description="Rahul's Scheme IDE!")
parser.add_argument("file",
                    type=argparse.FileType('r+'),
                    help="Scheme file to open")
parser.add_argument("-d", "--debug",
                    help="Enable debug mode",
                    action="store_true")
parser.add_argument("-t", "--terminal")
args = parser.parse_args()

local_server.start(args.file)
