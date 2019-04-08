import argparse
import json
import os

import local_server
import log
from formatter import prettify

parser = argparse.ArgumentParser(description="CS61A Scheme Editor - Spring 2019")
group = parser.add_mutually_exclusive_group()
group.add_argument("-f", "--files",
                   type=argparse.FileType('r+'),
                   help="Scheme files to test",
                   metavar="FILE",
                   nargs='*')
group.add_argument("-nb", "--nobrowser",
                   help="Do not open a new browser window.",
                   action="store_true")
group.add_argument("-d", "--dotted",
                   help="Enable dotted lists",
                   action="store_true")
group.add_argument("-p", "--port",
                   type=int,
                   default=31415,
                   help="Choose the port to access the editor")
group = parser.add_mutually_exclusive_group()
group.add_argument("-r", "--reformat",
                   type=argparse.FileType('a+'),
                   help="Reformat input files",
                   nargs=2,
                   metavar=('SOURCE', 'DEST'))
args = parser.parse_args()

if args.reformat is not None:
    source, dest = args.reformat
    source.seek(0)
    dest.truncate(0)
    dest.write(prettify([source.read()]))
    source.close()
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
