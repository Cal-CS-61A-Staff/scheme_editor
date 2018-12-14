import os
import sys
from dataclasses import dataclass
from io import StringIO
from typing import Tuple, List

newdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/ok"
sys.path.append(newdir)
print(sys.path)

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
CASE_DATA = "case_data"
ERROR = "error"


@dataclass
class TestCase:
    problem: str
    suite: int
    case: int
    passed: bool
    elements: List[Tuple[str, List[str]]]

    def get_full_str(self):
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
        return "\n".join(out)

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


def parse_test_data(raw_out):
    blocks = raw_out.split("-" * 69)
    blocks = blocks[1:-1]  # cut off the header + footer
    cases = []
    for block in blocks:
        lines = block.strip().split("\n")
        categorized_lines = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line == "-- OK! --":
                continue
            elif i == 0:
                categorized_lines.append((CASE_DATA, line))
            elif line.startswith("scm> ") or line.startswith(".... "):
                categorized_lines.append((SCHEME_INPUT, line[5:]))
            elif line.startswith("# "):
                if line[1:].strip() == "Error: expected" or line[1:].strip() == "but got":
                    categorized_lines.append((ERROR_HEADER, line[1:].strip()))
                else:
                    categorized_lines.append((ERROR, line[1:].strip()))
            else:
                categorized_lines.append((OUTPUT, line))

        collapsed = []

        for line in categorized_lines:
            if not collapsed or collapsed[-1][0] != line[0]:
                collapsed.append((line[0], [line[1]]))
            else:
                collapsed[-1][1].append(line[1])

        elements = []
        error = False
        for i, (category, data) in enumerate(collapsed):
            if category == ERROR_HEADER:
                error = True
                elements.pop()
                elements.append((EXPECTED_OUTPUT, collapsed[i + 1][1]))
                elements.append((ACTUAL_OUTPUT, collapsed[i + 3][1]))
                break

            elements.append((category, data))

        vals = elements[0][1][0].split(" > ")
        problem = vals[0]
        suite = int(vals[1].split()[1])
        case = int(vals[2].split()[1])

        cases.append(TestCase(problem.replace("-", " ").title(), suite, case, not error, elements[1:]))

    out = []
    for case in cases:
        if not out or out[-1]["problem"] != case.problem:
            out.append({"problem": case.problem, "suites": [],
                        "passed": all(x.passed for x in cases if x.problem == case.problem)})
        if len(out[-1]["suites"]) != case.suite:
            out[-1]["suites"].append([])
        out[-1]["suites"][-1].append(case.export())

    return out
