import argparse
import local_server

parser = argparse.ArgumentParser(description="Rahul's Scheme IDE!")
parser.add_argument("file",
                    type=argparse.FileType('r+'),
                    help="Scheme file to open")
parser.add_argument("-d", "--debug",
                    help="Enable debug mode",
                    action="store_true")
parser.add_argument("-s", "--scm",
                    help="start SCM searcher",
                    action="store_true")
parser.add_argument("-t", "--terminal")
args = parser.parse_args()

file_name = args.file.name
args.file.close()
local_server.start(file_name)
