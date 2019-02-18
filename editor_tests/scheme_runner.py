import execution
import log
from scheme_exceptions import ParseError


def run_scm(code: str):
    try:
        log.logger.new_query()
        execution.string_exec(code, log.logger.out)
    except ParseError as e:
        return {"success": False, "out": [str(e)]}

    return log.logger.export()


def decode_case(case: str):
    with open(f"scm_tests/{case}.py"):
        f = str(f)
