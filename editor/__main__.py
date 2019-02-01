import argparse
import os

import local_server

parser = argparse.ArgumentParser(description="Rahul's Scheme IDE!")
parser.add_argument("-f", "--file",
                    type=argparse.FileType('r+'),
                    help="Scheme file to open")
parser.add_argument("-l", "--logging",
                    help="Print log statements",
                    action="store_true")
parser.add_argument("-p", "--port",
                    type=int,
                    default=31415,
                    help="Choose the port to access the editor")
args = parser.parse_args()

if args.file is not None:
    file_name = os.path.basename(args.file.name)
    args.file.close()
else:
    file_name = "hw10.scm"
local_server.start(file_name, args.port)
