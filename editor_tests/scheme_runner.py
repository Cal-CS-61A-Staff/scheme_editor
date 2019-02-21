import importlib
from abc import ABC
from collections import namedtuple

import sys
import os
sys.path.append(os.path.abspath('./editor'))
import execution
import log
from scheme_exceptions import ParseError

Query = namedtuple("Query", ["code", "expected"])
Response = namedtuple("Response", ["success", "message"])


class TestCase(ABC):
    def run(self):
        raise NotImplementedError()

    @staticmethod
    def compare(observed, expected):
        reduced_observed = {k: v for k, v in observed.items() if k in expected}
        assert reduced_observed == expected, f"\nObserved={reduced_observed}\nExpected={expected}"


class SchemeTestCase(TestCase):
    def __init__(self, queries, *, reset=True):
        self.queries = queries
        self.reset = reset

    def get_scm_response(self, code):
        try:
            if self.reset:
                log.logger = log.Logger()
                log.announce = log.logger.log
            log.logger.new_query()
            if isinstance(code, str):
                code = [code]
            execution.string_exec(code, log.logger.out)
        except ParseError as e:
            return {"success": False, "out": [str(e)]}

        return log.logger.export()

    def run(self):
        for query in self.queries:
            response = self.get_scm_response(query.code)
            self.compare(response, query.expected)


def run_case(case: str):
    sys.path.append(os.path.abspath('./editor_tests/scm_tests'))
    cases = __import__(f"case_{case}")
    for case in cases.cases:
        case.run()
