import argparse
import json
import os

import local_server
import log

parser = argparse.ArgumentParser(description="CS61A Scheme Editor - Spring 2019")
parser.add_argument("-f", "--files",
                    type=argparse.FileType('r+'),
                    help="Scheme files to test",
                    nargs='*')
parser.add_argument("-nb", "--nobrowser",
                    help="Do not open a new browser window.",
                    action="store_true")
parser.add_argument("-d", "--dotted",
                    help="Enable dotted lists",
                    action="store_true")
parser.add_argument("-p", "--port",
                    type=int,
                    default=31415,
                    help="Choose the port to access the editor")
args = parser.parse_args()

log.logger.dotted = args.dotted

configs = [f for f in os.listdir(os.curdir) if f.endswith(".ok")]

if args.files is not None:
    file_names = [os.path.basename(file.name) for file in args.files]
    for file in args.files:
        file.close()
else:
    file_names = []
    if len(configs) > 1:
        parser.error("Multiple okpy configs detected, files to be tested must be specified explicitly.")
    elif len(configs) > 0:
        with open(configs[0]) as f:
            file_names = json.loads(f.read())["src"]
local_server.start(file_names, args.port, not args.nobrowser)
