import importlib
from abc import ABC
from collections import namedtuple

import sys
import os
from typing import List

sys.path.append(os.path.abspath('./editor'))
import execution
import log
from scheme_exceptions import ParseError

Query = namedtuple("Query", ["code", "expected"])
Response = namedtuple("Response", ["success", "message"])


def out(*expected):
    return {"out": ["\n".join(expected) + "\n"]}


class TestCase(ABC):
    def run(self):
        raise NotImplementedError()

    @staticmethod
    def compare(observed, expected, code=""):
        for key in expected:
            if key == "out" and "Error" in expected[key][0]:
                assert "Traceback" in observed[key][0]
            else:
                assert observed[key] == expected[key], \
                    f"Code: {code}\nObserved: \n{repr(observed[key])}\nExpected: \n{repr(expected[key])}"


class SchemeTestCase(TestCase):
    """
    Self-contained test case, runs with a single fresh logger
    Simulates each Query sent in sequence from the client
    Queries represent a single code execution block
    """
    def __init__(self, queries):
        self.queries: List[Query] = queries

    def __repr__(self):
        return "SchemeTestCase(" + repr(self.queries) + ")"

    @staticmethod
    def get_scm_response(code, reset, global_frame=None):
        try:
            if reset:
                log.logger = log.Logger()
                log.logger.autodraw = False
                log.announce = log.logger.log
            if global_frame is not None:
                log.logger.new_query(log.logger.frame_lookup[id(global_frame)])
            else:
                log.logger.new_query()
            if isinstance(code, str):
                code = [code]
            else:
                code = ["\n".join(code)]
            execution.string_exec(code, log.logger.out, global_frame)
        except ParseError as e:
            return {"success": False, "out": [str(e)]}

        out = log.logger.export()
        return out

    def run(self):
        global_frame = None
        for query in self.queries:
            response = self.get_scm_response(query.code, query is self.queries[0], global_frame)
            self.compare(response, query.expected, query.code)
            if global_frame is None:
                global_frame = log.logger.frame_lookup[response["globalFrameID"]].base


def run_case(case: str):
    sys.path.append(os.path.abspath('./editor_tests/scm_tests'))
    if not case.startswith("case"):
        case = "case_" + case
    if case.endswith(".py"):
        case = case[:-3]
    cases = __import__(f"{case}")
    for case in cases.cases:
        case.run()


def run_all_cases(path):
    if not path.startswith("/"):
        path = "/" + path
    files = filter(lambda x: x.lower().startswith("case"), os.listdir(os.curdir + "/editor_tests" + path))
    for file in files:
        print(file)
        run_case(file)
