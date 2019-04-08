import argparse
import json
import os

import local_server
import log
from formatter import prettify

parser = argparse.ArgumentParser(description="CS61A Scheme Editor - Spring 2019")

parser.add_argument("-f", "--files",
                    type=argparse.FileType('r+'),
                    help="Scheme files to test",
                    metavar="FILE",
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
parser.add_argument("-r", "--reformat",
                    type=argparse.FileType('a+'),
                    help="File to be reformatted.",
                    metavar='FILE')
parser.add_argument("-o", "--out",
                    type=argparse.FileType('w+'),
                    help="Write to separate output file")
args = parser.parse_args()

if args.reformat is not None:
    source = args.reformat
    if args.out is not None:
        dest = args.out
    else:
        dest = source
    source.seek(0)
    prettified = prettify([source.read()])
    dest.truncate(0)
    dest.write(prettified)
    source.close()
    if args.out is not None:
        dest.close()
    exit()

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
            file_names = [name for name in json.loads(f.read())["src"] if name.endswith(".scm")]
local_server.start(file_names, args.port, not args.nobrowser)
