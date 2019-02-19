import os
import re
import sys
from dataclasses import dataclass
from typing import Tuple, List

import formatter

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
# noinspection PyUnresolvedReferences
import client
import logging
import sys

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
    elements: str

    def export(self):
        return {
            "code": self.elements,
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

def capture_output(console, lines):
    old_stdout = sys.stdout
    sys.stdout = out = PrintCapture()
    result = console._interpret_lines(lines)
    sys.stdout = old_stdout
    return result, out.log

@dataclass
class FailureInSetup:
    setup_out: str

    @property
    def success(self):
        return False

    @property
    def output(self):
        return "; There was an error in running the setup code (probably in loading your file)\n\n" + "".join(self.setup_out)

@dataclass
class FullTestCase:
    success: bool
    interpret_out: str

    @property
    def output(self):
        result, _ = process_test_errors(collapse_test_lines(categorize_test_lines(self.interpret_out)))
        return format(result)

def chunked_input(lines):
    chunk = []
    for line in lines:
        if isinstance(line, str):
            yield chunk
            chunk = []
        chunk.append(line)
    yield chunk

def process_case(case):
    setup_success, setup_out = capture_output(case.console, case.setup.splitlines())
    if not setup_success or "Traceback" in "".join(setup_out):
        return FailureInSetup(setup_out)
    interpret_success_overall = True
    interpret_out_overall = []
    for chunk in chunked_input(case.lines + case.teardown.splitlines()):
        interpret_success, interpret_out = capture_output(case.console, chunk)
        interpret_success_overall = interpret_success_overall and interpret_success
        interpret_out_overall += interpret_out
    return FullTestCase(
        interpret_success_overall,
        interpret_out_overall)

def format(overall_lines):
    out = []
    for tag, lines in overall_lines:
        if tag == SCHEME_INPUT:
            out.append("\n".join(lines))
        elif tag in (OUTPUT, EXPECTED_OUTPUT):
            prefix = "; expect "
            for ret in lines:
                out.append(prefix + ret)
                prefix = ";" + " " * (len(prefix) - 1)
        elif tag == ACTUAL_OUTPUT:
            lines = [y for x in lines for y in x.split("\n")]
            prefix = "; actually received "
            if lines[0].startswith("Traceback"):
                lines[2] = lines[2].split(": ", 2)[1]
                lines[:] = ["SchemeError:\n; " + "\n; ".join(lines[2:])]
            for ret in lines:
                out.append(prefix + ret)
                prefix = ";" + " " * (len(prefix) - 1)
    return formatter.prettify(["\n".join(out)])


def run_tests():
    LOGGING_FORMAT = '%(levelname)s  | %(filename)s:%(lineno)d | %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)
    log = logging.getLogger('client')  # Get top-level logger

    # noinspection PyUnresolvedReferences
    from client.cli.ok import parse_input
    from client.sources.ok_test.scheme import SchemeSuite
    log.setLevel(logging.ERROR)

    args = parse_input(["--all", "--verbose", "--local"])

    assign = assignment.load_assignment(None, args)

    result = []
    for test in assign.specified_tests:
        for suiteno, suite in enumerate(test.suites):
            assert isinstance(suite, SchemeSuite)
            for caseno, case in enumerate(suite.cases):
                procd_case = process_case(case)
                result.append(TestCase(test.name, suiteno + 1, caseno + 1, procd_case.success, procd_case.output))

    return result


def categorize_test_lines(lines):
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line == "-- OK! --":
            continue
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

def parse_test_data(cases):
    out = []
    for case in cases:
        if not out or out[-1]["problem"] != case.problem:
            out.append({"problem": case.problem, "suites": [],
                        "passed": all(x.passed for x in cases if x.problem == case.problem)})
        if len(out[-1]["suites"]) != case.suite:
            out[-1]["suites"].append([])
        out[-1]["suites"][-1].append(case.export())

    return out
