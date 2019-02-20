import importlib
from abc import ABC

import execution
import log
from scheme_exceptions import ParseError


class TestCase(ABC):
    def run(self):
        raise NotImplementedError()

    @staticmethod
    def compare(observed, expected):
        for key, val in expected.items():
            assert observed[key] == val


class SchemeTestCase(TestCase):
    def __init__(self, queries, *, reset=True):
        self.queries = queries
        self.reset = reset

    def get_scm_response(self, code):
        try:
            if self.reset:
                log.logger = log.Logger()
            log.logger.new_query()
            execution.string_exec(code, log.logger.out)
        except ParseError as e:
            return {"success": False, "out": [str(e)]}

        return log.logger.export()

    def run(self):
        for query in self.queries:
            response = self.get_scm_response(query.code)
            self.compare(response, query.expected)


def run_case(case: str):
    importlib.import_module(f"scm_tests/{case}.py").run()
