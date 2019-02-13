import formatter
import os
import sys
import re
from dataclasses import dataclass
from io import StringIO
from typing import Tuple, List

newdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/ok"
sys.path.append(newdir)

# CODE TAKEN FROM OK-CLIENT : https://github.com/okpy/ok-client/blob/master/client/cli/ok.py

##############
# OKPY IMPORTS
# noinspection PyUnresolvedReferences
from client import exceptions as ex
# noinspection PyUnresolvedReferences
from client.api import assignment
# noinspection PyUnresolvedReferences
from client.cli.common import messages
# noinspection PyUnresolvedReferences
from client.utils import auth
# noinspection PyUnresolvedReferences
from client.utils import output
# noinspection PyUnresolvedReferences
from client.utils import software_update

from datetime import datetime
import argparse
# noinspection PyUnresolvedReferences
import client
import logging
import os
import sys
import struct
#############

SCHEME_INPUT = "scheme_input"
OUTPUT = "output"
ACTUAL_OUTPUT = "actual_output"
EXPECTED_OUTPUT = "expected_output"

ERROR_HEADER = "error_header"
LOAD_ERROR_HEADER = "load_error_header"
CASE_DATA = "case_data"
ERROR = "error"


ERROR_EOF_MESSAGE = "Error: unexpected end of file"

@dataclass
class TestCase:
    problem: str
    suite: int
    case: int
    passed: bool
    elements: List[Tuple[str, List[str]]]

    def get_full_str(self):
        inp = []
        out = []
        for elem in self.elements:
            if elem[0] == SCHEME_INPUT:
                out.append("\n".join(elem[1]))
            elif elem[0] in (OUTPUT, EXPECTED_OUTPUT):
                prefix = "; expect "
                for ret in elem[1]:
                    out.append(prefix + ret)
                    prefix = ";" + " " * (len(prefix) - 1)
            elif elem[0] == ACTUAL_OUTPUT:
                prefix = "; actually received "
                if elem[1][0].startswith("Traceback"):
                    elem[1][2] = elem[1][2].split(": ", 2)[1]
                    elem[1][:] = ["SchemeError:\n; " + "\n; ".join(elem[1][2:])]
                for ret in elem[1]:
                    out.append(prefix + ret)
                    prefix = ";" + " " * (len(prefix) - 1)
        return formatter.prettify(["\n".join(out)])

    def export(self):
        return {
            "code": self.get_full_str(),
            "passed": self.passed
        }


class PrintCapture:
    def __init__(self):
        self.log = []

    def write(self, message):
        self.log.append(message)
        sys.__stdout__.write(message)

    def flush(self):
        sys.__stdout__.flush()


def run_tests():
    LOGGING_FORMAT = '%(levelname)s  | %(filename)s:%(lineno)d | %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)
    log = logging.getLogger('client')  # Get top-level logger

    # noinspection PyUnresolvedReferences
    from client.cli.ok import parse_input
    log.setLevel(logging.ERROR)

    args = parse_input(["--all", "--verbose", "--local"])

    old_stdout = sys.stdout
    sys.stdout = out = PrintCapture()

    assign = assignment.load_assignment(None, args)

    msgs = messages.Messages()
    for name, proto in assign.protocol_map.items():
        log.info('Execute {}.run()'.format(name))
        proto.run(msgs)

    msgs['timestamp'] = str(datetime.now())

    if assign:
        assign.dump_tests()

    sys.stdout = old_stdout
    return "\n".join(out.log)


def categorize_test_lines(lines):
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line == "-- OK! --":
            continue
        elif i == 0:
            yield CASE_DATA, line
        elif line.startswith("scm> ") or line.startswith(".... "):
            yield SCHEME_INPUT, line[5:]
        elif line.startswith("# "):
            if line[1:].strip() == "Error: expected" or line[1:].strip() == "but got":
                yield ERROR_HEADER, line[1:].strip()
            elif line[1:].strip() == ERROR_EOF_MESSAGE:
                yield LOAD_ERROR_HEADER, line[1:].strip()
            else:
                yield ERROR, line[1:].strip()
        else:
            yield OUTPUT, line

def collapse_test_lines(categorized_lines):
    collapsed = []
    for category, line in categorized_lines:
        if not collapsed or collapsed[-1][0] != category:
            collapsed.append((category, [line]))
        else:
            collapsed[-1][1].append(line)
    return collapsed

def process_test_errors(collapsed):
    elements = []
    error = False
    for i, (category, data) in enumerate(collapsed):
        if category == ERROR_HEADER:
            error = True
            elements.pop()
            elements.append((EXPECTED_OUTPUT, collapsed[i + 1][1]))
            elements.append((ACTUAL_OUTPUT, collapsed[i + 3][1]))
            break
        elif category == LOAD_ERROR_HEADER:
            error = True
            elements.append((EXPECTED_OUTPUT, ['']))
            elements.append((ACTUAL_OUTPUT, [ERROR_EOF_MESSAGE]))
            break

        elements.append((category, data))
    return elements, error

def create_test_case_from_block(block):
    lines = block.strip().split("\n")

    categorized_lines = list(categorize_test_lines(lines))
    collapsed = collapse_test_lines(categorized_lines)
    elements, error = process_test_errors(collapsed)

    (_, [header]), *this_case = elements

    match = re.match(r'(\S+) > Suite (\S+) > Case (\S+)', header)

    problem = match.group(1).replace("-", " ").title()
    suite = int(match.group(2))
    case = int(match.group(3))
    return TestCase(problem, suite, case, not error, this_case)

def parse_test_data(raw_out):
    blocks = raw_out.split("-" * 69)
    blocks = blocks[1:-1]  # cut off the header + footer
    cases = [create_test_case_from_block(block) for block in blocks]

    out = []
    for case in cases:
        if not out or out[-1]["problem"] != case.problem:
            out.append({"problem": case.problem, "suites": [],
                        "passed": all(x.passed for x in cases if x.problem == case.problem)})
        if len(out[-1]["suites"]) != case.suite:
            out[-1]["suites"].append([])
        out[-1]["suites"][-1].append(case.export())

    return out
