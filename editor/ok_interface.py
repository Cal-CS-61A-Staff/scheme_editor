import formatter
import os
import re
import sys
from collections import namedtuple
from abc import ABCMeta, abstractmethod

from scheme_exceptions import TerminatedError

newdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/ok"
sys.path.append(newdir)

# CODE TAKEN FROM OK-CLIENT : https://github.com/okpy/ok-client/blob/master/client/cli/ok.py

FAILURE_SETUP_HEADER = '''; There was an error in running the setup code (probably in loading your file)
; Raw ok output follows'''

FAILURE_SETUP_FOOTER = "; Raw ok output over"


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
    if str(TerminatedError()) in "".join(out.log):
        raise TerminatedError
    return result, out.log


class PromptOutput(metaclass=ABCMeta):
    @abstractmethod
    def representation(self):
        pass

    @abstractmethod
    def success(self):
        pass


class AreDifferent(PromptOutput, namedtuple('AreDifferent', ['prompt', 'expected', 'actual'])):
    def representation(self):
        return "{expected}\n{actual}\n{prompt}".format(
            prompt=self.prompt,
            expected=pad("; Expected: ", ";", self.expected),
            actual=pad("; Actual  : ", ";", self.actual)
        )

    def success(self):
        return False


class Error(PromptOutput, namedtuple('PromptOutput', ['prompt', 'error'])):
    def representation(self):
        return "{error}\n{prompt}".format(
            error=pad("; Error: ", ";", self.error),
            prompt=self.prompt
        )

    def success(self):
        return False


class Same(PromptOutput, namedtuple('Same', ['prompt', 'output'])):
    def representation(self):
        return "{output}\n{prompt}".format(
            prompt=self.prompt,
            output=pad("; Success: ", ";", self.output)
        )

    def success(self):
        return True


class Locked(PromptOutput, namedtuple('Locked', [])):
    def representation(self):
        return "; Run python ok -u to unlock test case. \n (error \"Test case locked!\")"

    def success(self):
        return False


class TestCaseResult(namedtuple('TestCaseResult', ['cases_passed', 'cases_out', 'setup_out'])):

    @property
    def success(self):
        return self.setup_out.success() and self.cases_passed

    @property
    def output(self):
        result = ""
        if self.setup_out.success():
            result += self.setup_out.prompt
        else:
            result += self.setup_out.representation()
        result += "\n\n"
        result += "\n\n".join(x.representation() for x in self.cases_out)
        return formatter.prettify([result])

    @property
    def dictionary(self):
        return {
            "code": self.output,
            "passed": self.success
        }


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


def process(output, success):
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
    if not success:
        try:
            expected_index = next(idx for idx, line in enumerate(lines) if "# Error: expected" in line)
            but_got_idx = next(idx for idx, line in enumerate(lines) if "# but got" in line)
        except StopIteration:
            breakpoint()
        expected = remove_comments_and_combine(lines[expected_index + 1:but_got_idx])
        actual = remove_comments_and_combine(lines[but_got_idx + 1:])
        actual = re.sub(r"Traceback.*\n\.\.\.\n(.*)", r"\1", actual)
        if re.match("[0-9a-f]{32}", expected):  # looks like a hash
            return Locked()
        else:
            return AreDifferent("\n".join(prompt), expected, actual)
    elif "Traceback" in result or "# Error:" in result:
        return Error("\n".join(prompt).strip("\n"), result)
    else:
        return Same("\n".join(prompt), result.strip())


def process_case(case):
    setup_success, setup_out = capture_output(case.console, case.setup.splitlines())
    setup_out = "".join(setup_out)
    if not setup_success:
        return TestCaseResult(setup_success, [], process(setup_out, True))
    interpret_success_overall = True
    interpret_out_overall = []
    for chunk in chunked_input(case.lines + case.teardown.splitlines()):
        interpret_success, interpret_out = capture_output(case.console, chunk)
        interpret_success_overall = interpret_success_overall and interpret_success
        interpret_out_overall.append(process(interpret_out, interpret_success))

    if "Traceback" in setup_out:
        return TestCaseResult(False, interpret_out_overall, process(setup_out, True))
    return TestCaseResult(interpret_success_overall, interpret_out_overall, process(setup_out, True))


def reload_tests():
    for testname in filter(lambda x: x.lower().endswith(".py"), os.listdir(os.curdir + "/tests")):
        testname = "tests." + testname[:-3]
        if testname in sys.modules:
            del sys.modules[testname]


def run_tests():
    reload_tests()

    # noinspection PyUnresolvedReferences
    from client.api import assignment

    import logging

    LOGGING_FORMAT = '%(levelname)s  | %(filename)s:%(lineno)d | %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)
    log = logging.getLogger('client')  # Get top-level logger

    # noinspection PyUnresolvedReferences
    from client.cli.ok import parse_input
    # noinspection PyUnresolvedReferences
    from client.sources.ok_test.scheme import SchemeSuite
    log.setLevel(logging.ERROR)

    args = parse_input(["--all", "--verbose"])

    assign = assignment.load_assignment(None, args)

    try:
        result = []
        for test in assign.specified_tests:
            suites = []
            for suite in test.suites:
                assert isinstance(suite, SchemeSuite)
                suites.append([process_case(case).dictionary for case in suite.cases])
            result.append({
                "problem": test.name.replace("-", " ").title(),
                "suites": suites,
                "passed": all(x['passed'] for t in suites for x in t)
            })
        return result
    except TerminatedError:
        return [{'problem': "Tests Terminated by User", 'suites': [], 'passed': False}]
