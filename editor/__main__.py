import argparse
import json
import os

import local_server

parser = argparse.ArgumentParser(description="Rahul's Scheme IDE!")
parser.add_argument("-f", "--files",
                    type=argparse.FileType('r+'),
                    help="Scheme files to test",
                    nargs='*')
parser.add_argument("-l", "--logging",
                    help="Print log statements",
                    action="store_true")
parser.add_argument("-p", "--port",
                    type=int,
                    default=31415,
                    help="Choose the port to access the editor")
args = parser.parse_args()

configs = [f for f in os.listdir(os.curdir) if f.endswith(".ok")]

if args.files is not None:
    file_names = [os.path.basename(file.name) for file in args.files]
    args.file.close()
else:
    if len(configs) != 1:
        raise ValueError("Unable to resolve okpy configs, please specify files to be tested explicitly.")
    with open(configs[0]) as f:
        file_names = json.loads(f.read())["src"]
local_server.start(file_names, args.port)
