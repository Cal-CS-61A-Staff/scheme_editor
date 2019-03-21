import argparse
import json
import os

import local_server

parser = argparse.ArgumentParser(description="CS61A Scheme Editor - Spring 2019")
parser.add_argument("-f", "--files",
                    type=argparse.FileType('r+'),
                    help="Scheme files to test",
                    nargs='*')
parser.add_argument("-nt", "--notests",
                    help="Do not interact with OKPy.",
                    action="store_false")
parser.add_argument("-nb", "--nobrowser",
                    help="Do not open a new browser window.",
                    action="store_false")
parser.add_argument("-p", "--port",
                    type=int,
                    default=31415,
                    help="Choose the port to access the editor")
args = parser.parse_args()

configs = [f for f in os.listdir(os.curdir) if f.endswith(".ok")]

if args.files is not None:
    file_names = [os.path.basename(file.name) for file in args.files]
    for file in args.files:
        file.close()
else:
    if len(configs) != 1:
        parser.error("Unable to resolve okpy configs, files to be tested must be specified explicitly.")
    with open(configs[0]) as f:
        file_names = json.loads(f.read())["src"]
local_server.start(file_names, args.port, args.nobrowser)
