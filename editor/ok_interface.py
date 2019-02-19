import os
import re
import sys
from dataclasses import dataclass
from typing import Tuple, List
from abc import ABCMeta, abstractmethod

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

class PromptOutput(metaclass=ABCMeta):
    @abstractmethod
    def represenation(self):
        pass

@dataclass
class FullTestCase:
    success: bool
    interpret_out: List[PromptOutput]

    @property
    def output(self):
        return "\n\n".join(x.represenation() for x in self.interpret_out)

def chunked_input(lines):
    chunk = []
    for line in lines:
        chunk.append(line)
        if not isinstance(line, str):
            yield chunk
            chunk = []

def remove_comments_and_combine(lines):
    result = []
    for line in lines:
        if not line:
            continue
        if line[0] == "#":
            line = line[1:]
        line = line.strip()
        result.append(line)
    return "\n".join(result)

def pad(first_header, later_header, string):
    assert len(later_header) <= len(first_header)
    later_header += " " * (len(first_header) - len(later_header))
    lines = string.split("\n")
    lines[0] = first_header + lines[0]
    for i in range(1, len(lines)):
        lines[i] = later_header + lines[i]
    return "\n".join(lines)

@dataclass
class AreDifferent(PromptOutput):
    prompt: str
    expected: str
    actual: str
    def represenation(self):
        return "{prompt}\n{expected}\n{actual}".format(
            prompt=self.prompt,
            expected=pad("; expected ", ";", self.expected),
            actual  =pad("; actual   ", ";", self.actual)
        )

@dataclass
class Same(PromptOutput):
    prompt: str
    output: str
    def represenation(self):
        return "{prompt}\n{output}".format(
            prompt=self.prompt,
            output=pad("; output ", ";", self.output)
        )

def process(output):
    prompt = []
    lines = "".join(output).split("\n")
    start_idx = len(lines)
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if line.startswith("scm> ") or line.startswith(".... "):
            prompt.append(line[5:])
        else:
            start_idx = idx
            break
    result = "\n".join(lines[start_idx:])
    if "# Error: expected" in result:
        expected_index = next(idx for idx, line in enumerate(lines) if "# Error: expected" in line)
        but_got_idx = next(idx for idx, line in enumerate(lines) if "# but got" in line)
        expected = remove_comments_and_combine(lines[expected_index + 1:but_got_idx])
        actual = remove_comments_and_combine(lines[but_got_idx + 1:])
        actual = re.sub(r"Traceback.*\n\.\.\.\n(.*)", r"\1", actual)
        return AreDifferent("\n".join(prompt), expected, actual)
    else:
        return Same("\n".join(prompt), result.strip())


def process_case(case):
    setup_success, setup_out = capture_output(case.console, case.setup.splitlines())
    if not setup_success or "Traceback" in "".join(setup_out):
        return FailureInSetup(setup_out)
    interpret_success_overall = True
    interpret_out_overall = []
    for chunk in chunked_input(case.lines + case.teardown.splitlines()):
        interpret_success, interpret_out = capture_output(case.console, chunk)
        interpret_success_overall = interpret_success_overall and interpret_success
        interpret_out_overall.append(process(interpret_out))
    return FullTestCase(
        interpret_success_overall,
        interpret_out_overall)

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
